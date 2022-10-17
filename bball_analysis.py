import pandas as pd
import numpy as np
import io

class bb_picker:

    def __init__(self, make_df = False):

        self.df_22 = pd.read_csv("projections_22_23.csv")
        self.df_21 = pd.read_csv("2021_stats_full.csv")
        self.make_df = make_df
        self.totals_cols = ["PTS",
                            "REB",
                            "AST",
                            "BLK",
                            "STL",
                            "3PM",
                            "GP",
                            ]

    def format_df(self):

        self.df_22["PLAYER"] = self.df_22["PLAYER"].str.split("(").str[0]
        self.df_22["PLAYER"] = self.df_22["PLAYER"].apply(lambda x: str(x).replace(u'\xa0', u''))

    def format_2021_stats(self):
        self.df_21 = self.df_21.dropna(subset = ["NAME"])

        players_list = self.df_22["PLAYER"].unique()

        def _rename_players(name, players_list):
            print(name)
            match = ""
            for player in players_list:
                if player in name:
                    match = player
            
            return match
        
        self.df_21["PLAYER"] = self.df_21.apply(lambda row: _rename_players(row['NAME'], players_list), axis = 1)
        self.df_21 = self.df_21[["PLAYER", "FGA", "FTA"]]
        print(self.df_21.head())

    def join_dfs(self):
        self.df = pd.merge(self.df_22, self.df_21, how = "left", on = "PLAYER")

    def format_joined_df(self):

        low_fg = self.df["FGA"].mean()
        low_ft = self.df["FTA"].mean()
        self.df["FGA"] = np.where(self.df["FGA"].isna(), low_fg, self.df["FGA"])
        self.df["FTA"] = np.where(self.df["FTA"].isna(), low_ft, self.df["FTA"])
        self.df.to_csv("2022_2023_final_df.csv")

    def get_averages(self):
        if not self.make_df:
            self.players_df = pd.read_csv("2022_2023_final_df.csv")
        else:
            self.players_df = self.df
        
        top_150_df = self.players_df.head(150)
        def _weighted_avg(total_col, percentage_col):
            top_150_df[total_col+"_weighted"] = top_150_df[total_col]*top_150_df[percentage_col]
            avg = top_150_df[total_col+"_weighted"].sum()/top_150_df[total_col].sum()
            print(avg)
            return avg
        fg_avg = _weighted_avg("FGA", "FG%")
        ft_avg = _weighted_avg("FTA", "FT%")

        self.avg_dict = {}

        self.avg_dict["FG%"] = fg_avg
        self.avg_dict["FT%"] = ft_avg

        for col in self.totals_cols:

            avg = top_150_df[col].mean()
            self.avg_dict[col] = avg

    def picker(self):

        players_df = self.players_df
        print(players_df.head())
        
        percent_dict = {"FG%":"FGA", 
                        "FT%": "FTA"}

        for col in self.cols:

            players_df[col] = pd.to_numeric(players_df[col], errors='coerce')

        drafted_players = players_df.head(150)
        #print(list(drafted_players))
        
        averaged_list = []
        
        for col in self.cols:

            averaged_list.append(drafted_players[col].mean())
            print(col, ": ", drafted_players[col].mean())

        #print(averaged_list)

        counter = 0

        col_subset = ["PLAYER",
                        "3PM",
                        'PTS', 
                        'REB', 
                        'AST', 
                        'STL', 
                        'BLK',
                        "GP",
                        ]

        drafted_players = drafted_players[col_subset]

        addative_df = pd.DataFrame(columns=col_subset)
        
        while counter < 13:

            player_taken = input("Which player did you draft?")

            player_list = players_df["PLAYER"].unique()

            if player_taken in player_list:

                drafted_player_df = players_df[players_df["PLAYER"] == player_taken]

                drafted_player_df = drafted_player_df[col_subset]

                addative_df = addative_df.append(drafted_player_df)

                counter += 1

                for col, average in zip(self.cols, averaged_list):
                        #print(col, addative_df[col].sum(), average,counter)

                        print(col, 
                            round((1+(addative_df[col].sum() - average*counter)/average)*100, 1)
                            )
            else:
                print("player not found, try again")
                continue


if __name__ == "__main__":
    
    bp = bb_picker(make_df = False)

    if bp.make_df:
        bp.format_df()
        bp.format_2021_stats()
        bp.join_dfs()
        bp.format_joined_df()
    bp.get_averages()
    #bp.picker()