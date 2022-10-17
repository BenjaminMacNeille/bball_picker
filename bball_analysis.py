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
        
        top_150_df = self.players_df.head(120)
        def _weighted_avg(total_col, percentage_col):
            top_150_df[total_col+"_weighted"] = top_150_df[total_col]*top_150_df[percentage_col]
            avg = top_150_df[total_col+"_weighted"].sum()/top_150_df[total_col].sum()
            return avg
        self.fg_avg = _weighted_avg("FGA", "FG%")
        self.ft_avg = _weighted_avg("FTA", "FT%")

        self.avg_dict = {}

        self.avg_dict["FG%"] = self.fg_avg
        self.avg_dict["FT%"] = self.ft_avg

        for col in self.totals_cols:

            avg = top_150_df[col].mean()
            self.avg_dict[col] = avg

    def picker(self):

        players_df = self.players_df

        players_df = players_df[['PLAYER', 'PTS', 'REB', 'AST', 
                                'BLK', 'STL', 'FG%', 'FT%',
                                '3PM', 'GP', 'FGA', 'FTA']]
        print(players_df.head(50))
        
        
        percent_dict = {"FG%":"FGA", 
                        "FT%": "FTA"}

        for col in self.totals_cols:

            players_df[col] = pd.to_numeric(players_df[col], errors='coerce')

        drafted_players = players_df.head(120)
        #print(list(drafted_players))
        
        averaged_list = []
        
        for perc_col, att_col in percent_dict.items():
            players_df[att_col] = round(players_df[att_col], 3)

        for col in self.totals_cols:
            if col != "GP":
                players_df[col] = round(players_df[col]/players_df["GP"],3)
                drafted_players[col] = drafted_players[col]/drafted_players["GP"]

            averaged_list.append(drafted_players[col].mean())
            print(col, "NBA avg: ", round(drafted_players[col].mean(), 3))

        print("FG%",  "NBA avg: ", round(self.fg_avg, 3))
        print("FT%",  "NBA avg: ", round(self.ft_avg, 3))

        counter = 0

        col_subset = ["PLAYER",
                        'PTS', 
                        'REB', 
                        'AST', 
                        'STL', 
                        'BLK',
                        "3PM",
                        "FGA",
                        "FG%",
                        "FTA",
                        "FT%",
                        "GP",
                        ]
        players_df = players_df[col_subset]
        drafted_players = drafted_players[col_subset]

        addative_df = pd.DataFrame(columns=col_subset)
        
        while counter < 13:
            print("\n")
            drafted = input("Is this your draft pick? (y/n)")

            if drafted == "y":
                
                print(players_df.head(50))
                print("\n")
                for col in self.totals_cols:
                    print(col," : ", round(addative_df[col].mean(), 3), "  NBA avg: ", round(drafted_players[col].mean(), 3))

                def weighted_avg(total_col, percentage_col):
                    try:
                        addative_df[total_col+"_weighted"] = addative_df[total_col]*addative_df[percentage_col]
                        avg = round(addative_df[total_col+"_weighted"].sum()/addative_df[total_col].sum(),3)
                        return avg
                    except:
                        return "NA"
                
                fg = weighted_avg("FGA","FG%")
                ft = weighted_avg("FTA","FT%")
                
                print("FG%"," : ", fg,"  NBA avg: ", round(self.fg_avg, 3))
                print("FT%"," : ", ft,"  NBA avg: ",round(self.ft_avg, 3))

                player_taken = input("Which player did you draft?")

                player_list = players_df["PLAYER"].unique()

                if player_taken in player_list:

                    drafted_player_df = players_df.loc[players_df["PLAYER"] == player_taken]

                    drafted_player_df = drafted_player_df[col_subset]

                    addative_df = addative_df.append(drafted_player_df)
                    

                    counter += 1

                    players_df = players_df[players_df["PLAYER"] != player_taken]
                    print("\n")
                    for col in self.totals_cols:
                            
                            print(col," : ", round(addative_df[col].mean(), 3),"  NBA avg: ", round(drafted_players[col].mean(), 3))
                    
                    def weighted_avg(total_col, percentage_col):
                        try:
                            addative_df[total_col+"_weighted"] = (addative_df[total_col]*addative_df[percentage_col])

                            avg = addative_df.loc[total_col+"_weighted"].sum()/addative_df[total_col].sum()
                            return avg
                        except:
                            return "NA"
                
                    fg = weighted_avg("FGA", "FG%")
                    ft = weighted_avg("FTA", "FT%")
                    
                    print("FG%"," : ", fg,"  NBA avg: ", round(self.fg_avg, 3))
                    print("FT%"," : ", ft,"  NBA avg: ",round(self.ft_avg, 3))

                else:
                    print("player not found, try again")
                    continue
            
            elif drafted == "n":

                #print(players_df.head(50))

                player_taken = input("Which player was drafted?")

                player_list = players_df["PLAYER"].unique()

                if player_taken in player_list:
                
                    players_df = players_df[players_df["PLAYER"] != player_taken]
                
                else:
                    print("player not found, try again")
                    continue
            else:
                print("invalid key, try again")
                continue


if __name__ == "__main__":
    
    bp = bb_picker(make_df = False)

    if bp.make_df:
        bp.format_df()
        bp.format_2021_stats()
        bp.join_dfs()
        bp.format_joined_df()
    bp.get_averages()
    bp.picker()