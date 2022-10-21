import pandas as pd
from datetime import date

'''
Generates a fantasy football draft cheat sheet and exports it to CSV file that user can
adjust in excel or numbers to their liking
Merges Fantasy Pros and Fantasy Footballers rankings and averages them for final ranking
Creates columns for player analysis that can be adjusted in final product
'''

#import 4 files (using seperate columns and data from each)
ffdf = pd.read_csv('FFB_top200.csv') #fantasy footballers top 200 rankings
fptdf = pd.read_csv('FPS_tots.csv') #fantasy pros total points rankings
fpadf = pd.read_csv('FPS_avgs.csv') #fantasy pros avergage points rankings
fpodf = pd.read_csv('FPS_overview.csv') #fantasy pros overview rankings

#global variables
ecr = 0
qbs = 0
rbs = 0
wrs = 0
tes = 0
qbs2 = 0
rbs2 = 0
wrs2 = 0
tes2 = 0
flex = 0
rank_counter = 0

#functions to be called later - summary of each in a larger file

def change_pos(posrnk):
    pos = posrnk[0:2]
    return pos


def gen_adp(eva):
    global ecr
    ecr +=1
    if eva == '-':
        return '-'
    return int(eva) + ecr


def update_name(player):
    punct = ['.',',',"'",'-']
    letter_list = [let.upper() for let in player if let not in punct]
    player_str = ''.join(letter_list)
    player_list = player_str.split()
    if len(player_list[0]) > 2:
        player_list[0] = player_list[0][0:3] 
    #makes first name only 3 letters (avoids abbreviated names like kenneth->ken, patrick->pat)
    if len(player_list) == 3:
        if len(player_list[-1]) < 4:
            player_list = player_list[0:-1]
        return ' '.join(player_list)
    else:
        return str(player_list[0]) + ' ' + str(player_list[1])


def projected_pos(pos):
    
    global qbs 
    global rbs
    global wrs
    global tes
    
    if str(pos) == 'QB':
        qbs +=1
        return pos + ' ' + str(qbs)
    elif str(pos) == 'RB':
        rbs +=1
        return pos + ' ' + str(rbs)
    elif str(pos) == 'WR':
        wrs +=1
        return pos + ' ' + str(wrs)
    elif str(pos) == 'TE':
        tes +=1
        return pos + ' ' + str(tes)


def last_season_pos(pos, total_points):
    
    global qbs2
    global rbs2
    global wrs2
    global tes2
    global flex
    
    if total_points == 0.0:
        return 'NA'
    elif str(pos) == 'QB':
        qbs2 +=1
        return pos + ' ' + str(qbs2)
    elif str(pos) == 'RB':
        flex +=1
        rbs2 +=1
        return pos + ' ' + str(rbs2) + ' ' + '(' + str(flex) + ')'
    elif str(pos) == 'WR':
        flex +=1
        wrs2 +=1
        return pos + ' ' + str(wrs2) + ' ' + '(' + str(flex) + ')'
    elif str(pos) == 'TE':
        flex +=1
        tes2 +=1
        return pos + ' ' + str(tes2) + ' ' + '(' + str(flex) + ')'


def last_vs_proj(finish, proj):
    if finish == 'NA':
        return 0
    else:
        finish_list = finish.split()
        proj_list = proj.split()
        value = int(proj_list[1]) - int(finish_list[1])
        return value 


def correlation(ffbs, fpros):
    return abs(ffbs-fpros)


def total_rank(x):
    global rank_counter
    rank_counter +=1
    return rank_counter


def rkvadp(rank, adp):
    if adp == '-':
        return '-'
    return int(adp) - int(rank)


#master function to adjust dataframes and utilize above functions in order to generate cheat sheet
def generate_draft_sheet():

	filt = (ffdf['Team'] == 'JAX')
	ffdf.loc[filt, 'Team'] = 'JAC'

	ffdf.rename(columns={'Name': 'PLAYER', 'Rank': 'FFB RK'},inplace=True)
	ffdf.columns = [x.upper() for x in ffdf.columns]
	ffdf.drop(columns=['JASON', 'MIKE', 'MARKERS', 'POSITION'], inplace=True)

	fpodf.drop(columns=['RK','TIERS','TEAM','SOS SEASON'], inplace=True)
	fpodf.rename(columns={'PLAYER NAME': 'PLAYER', 'BYE WEEK': 'BYE',
						  'ECR VS. ADP': 'ECR V ADP'},inplace=True)

	fpodf['POS'] = fpodf['POS'].apply(change_pos)

	fpadf.drop(columns=['RK','TIERS','TEAM','YDS','TDS','REC','YDS.1',
                    	'TDS.1','ATT','YDS.2','TDS.2'], inplace=True)
	fpadf.rename(columns={'PLAYER NAME': 'PLAYER', 'FAN PTS': 'PPG',},inplace=True)

	fpodf['ADP'] = fpodf['ECR V ADP'].apply(gen_adp)
	fpodf.drop(columns=['ECR V ADP'], inplace=True)

	fptdf.rename(columns={'RK': 'FPS RK',
	                      'TIERS': 'TIER',
	                      'PLAYER NAME': 'PLAYER',
	                      'FAN PTS': 'TOT PTS',
	                      'YDS': 'PYD',
	                      'TDS': 'PTD',
	                      'YDS.1': 'REC YD',
	                      'TDS.1': 'REC TD',
	                      'ATT': 'RUS ATT',
	                      'YDS.2': 'RUS YD',
	                      'TDS.2': 'RUS TD'}, inplace=True)

	fpdf = pd.merge(fptdf, fpadf, on='PLAYER')
	fpdf = pd.merge(fpdf, fpodf, on='PLAYER')

	ffdf['PLAYER'] = ffdf['PLAYER'].apply(update_name)
	fpdf['PLAYER'] = fpdf['PLAYER'].apply(update_name)

	fpdf['PLAYER POS TM'] = fpdf['PLAYER'] + ', ' + fpdf['POS'] + ', ' + fpdf['TEAM']
	ffdf['PLAYER POS TM'] = ffdf['PLAYER'] + ', ' + ffdf['POS'] + ', ' + ffdf['TEAM']

	ffdf.drop(columns=['PLAYER', 'POS', 'TEAM'], inplace=True)

	combined_df = pd.merge(fpdf, ffdf, on='PLAYER POS TM')

	combined_df['AVG RK'] = (combined_df['FPS RK'] + combined_df['FFB RK'])/2

	combined_df.sort_values(by=['AVG RK', 'ANDY'], inplace=True)

	combined_df['PROJ'] = combined_df['POS'].apply(projected_pos)

	combined_df.sort_values(by=['TOT PTS'], ascending=False, inplace=True)

	combined_df['FINISH'] = combined_df.apply(lambda x: last_season_pos(x['POS'], x['TOT PTS']), axis=1)

	combined_df.sort_values(by=['AVG RK', 'ANDY'], inplace=True)

	combined_df.drop(columns=['POS', 'PLAYER', 'TEAM'], inplace=True)
	combined_df.rename(columns={'PLAYER POS TM': 'PLAYER'},inplace=True)

	combined_df[['PLAYER','POS','TEAM']] = combined_df['PLAYER'].str.split(', ', expand=True)

	combined_df['VALUE'] = combined_df.apply(lambda x: last_vs_proj(x['FINISH'], x['PROJ']), axis=1)

	combined_df['RK'] = combined_df['PLAYER'].apply(total_rank)

	combined_df['RK V ADP'] = combined_df.apply(lambda x: rkvadp(x["RK"], x["ADP"]), axis=1)

	combined_df.set_index('RK', inplace=True)

	combined_df['DIFF'] = combined_df.apply(lambda x: correlation(x["FPS RK"], x["FFB RK"]), axis=1)

	combined_df = combined_df.reindex(columns=['TIER',
	                                           'PLAYER',
	                                           'TEAM',
	                                           'PROJ',
	                                           'AVG RK',
	                                           'FFB RK',
	                                           'FPS RK',
	                                           'DIFF',
	                                           'ANDY',
	                                           'ADP',
	                                           'RK V ADP',
	                                           'TOT PTS',
	                                           'PPG',
	                                           'FINISH',
	                                           'VALUE',
	                                           'REC',
	                                           'REC YD',
	                                           'REC TD',
	                                           'RUS ATT',
	                                           'RUS YD',
	                                           'RUS TD',
	                                           'PYD',
	                                           'PTD',
	                                           'POS',
	                                           'BYE',])

	today = date.today().strftime("%b-%d-%y")
	
	#generates new draft sheets exported to csv file
	combined_df.to_csv(f'{today}_AVGRanks.csv')

	return print('Draft sheet successfully generated')

generate_draft_sheet()
