import pandas as pd
import io

def initial_analysis():

    players_df = pd.read_csv("top_245_2021.csv")

    players_df["PLAYER"] = players_df["PLAYER"].str.replace("\s+\(.*$", "")
    players_df["PTS"] = players_df["PTS"].str.replace(",", "")

    #players_df["PLAYER"] = players_df["PLAYER"].str.split(' \s+\(')[0]

    #players_df["R"] = pd.to_numeric(players_df["R"], errors='coerce')
    #players_df["TOTAL"] = pd.to_numeric(players_df["TOTAL"], errors='coerce')
    #players_df["FG%"] = players_df["FG%"].apply(lambda x: x[:4])
    #players_df["FT%"] = players_df["FT%"].apply(lambda x: x[:4])

    print(players_df.head())
    
    cols = ["3PM",
            'PTS', 
            'TREB', 
            'AST', 
            'STL', 
            'BLK', 
            #'TOTAL'
            ]
    

    percent_cols = ["FG%", "FT%"]

    for col in cols:

        players_df[col] = pd.to_numeric(players_df[col], errors='coerce')

    drafted_players = players_df.head(150)
    #print(list(drafted_players))
    
    averaged_list = []
    
    for col in cols:

        averaged_list.append(drafted_players[col].mean())
        print(col, ": ", drafted_players[col].mean())

    #print(averaged_list)

    counter = 0

    col_subset = ["PLAYER",
                  "3PM",
                    'PTS', 
                    'TREB', 
                    'AST', 
                    'STL', 
                    'BLK',  
                #'TOTAL'
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

            for col, average in zip(cols, averaged_list):
                    #print(col, addative_df[col].sum(), average,counter)

                    print(col, 
                        round((1+(addative_df[col].sum() - average*counter)/average)*100, 1)
                        )
        
            
        else:
            print("player not found, try again")
            continue


if __name__ == "__main__":
    
    initial_analysis()