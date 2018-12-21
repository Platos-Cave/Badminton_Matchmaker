
# The original code for reference
# people = pd.read_csv('final_arrivals.csv')
# non_players = ['_', "__", "--", "---","Dummy1", "Dummy2", "Lance"]
# people_2 = people[~people['NAME'].isin(non_players)]
# people_2['NAME'] = people_2['NAME'].replace({'Andrew B': 'Andrew', 'jino': 'Jino', ' RJ': 'RJ'})
# a = people_2['NAME'].value_counts()
# a = a/51
# a = a.to_dict()

arrival_probs = {'David': 1.0,
 'Desmond': 0.9607843137254902,
 'Munir': 0.9411764705882353,
 'Henry': 0.9215686274509803,
 'Adnan': 0.8627450980392157,
 'Tallat': 0.7647058823529411,
 'Muti': 0.7450980392156863,
 'Zahid': 0.6078431372549019,
 'Gabhriel': 0.5294117647058824,
 'Bonnie': 0.5294117647058824,
 'Ronny': 0.5098039215686274,
 'Stewart': 0.49019607843137253,
 'Andrew': 0.47058823529411764,
 'Marion': 0.43137254901960786,
 'Stuart': 0.43137254901960786,
 'Jack': 0.39215686274509803,
 'Richard H': 0.37254901960784315,
 'Henry M': 0.35294117647058826,
 'Ken': 0.3333333333333333,
 'Michael': 0.3333333333333333,
 'Gary': 0.3333333333333333,
 'Paul': 0.3137254901960784,
 'Kelly': 0.3137254901960784,
 'Ram': 0.29411764705882354,
 'Gary D': 0.27450980392156865,
 'Sonam': 0.27450980392156865,
 'Kieran': 0.27450980392156865,
 'Sundeep': 0.27450980392156865,
 'Brodie': 0.2549019607843137,
 'Sumati': 0.2549019607843137,
 'RJ': 0.2549019607843137,
 'Mark': 0.23529411764705882,
 'Richard': 0.23529411764705882,
 'Cyp': 0.23529411764705882,
 'Zed': 0.21568627450980393,
 'Praveen': 0.21568627450980393,
 'Elizabeth': 0.19607843137254902,
 'David 2': 0.19607843137254902,
 'Annie': 0.19607843137254902,
 'Bob': 0.17647058823529413,
 'Emily': 0.17647058823529413,
 'Tess': 0.17647058823529413,
 'Jeremy': 0.1568627450980392,
 'Erwin': 0.1568627450980392,
 'Choon': 0.13725490196078433,
 'Ohyoung': 0.13725490196078433,
 'Alex': 0.13725490196078433,
 'Nick': 0.13725490196078433,
 'Kiran': 0.13725490196078433,
 'Kevin': 0.13725490196078433,
 'Cory': 0.11764705882352941,
 'Anil': 0.11764705882352941,
 'Andrew H': 0.09803921568627451,
 'Mohsam': 0.09803921568627451,
 'Guzni': 0.09803921568627451,
 'Denise': 0.0784313725490196,
 'Jino': 0.0784313725490196,
 'Song': 0.058823529411764705,
 'Tushar': 0.058823529411764705,
 'Argus': 0.058823529411764705,
 'Albert': 0.0392156862745098,
 'Tara': 0.0392156862745098,
 'Dennis': 0.0392156862745098,
 'Ronnie': 0.0392156862745098,
 'Bala': 0.0392156862745098,
 'John': 0.0392156862745098,
 'Marlene': 0.0392156862745098,
 'Joe': 0.0392156862745098,
 'Suzie': 0.0392156862745098,
 'Tracy': 0.0196078431372549,
 'Falsal': 0.0196078431372549,
 'Charlotta': 0.0196078431372549,
 'Kat': 0.0196078431372549,
 'Ramya': 0.0196078431372549,
 'Joseph': 0.0196078431372549,
 'Sam': 0.0196078431372549,
 'Kate': 0.0196078431372549,
 'Franceska': 0.0196078431372549,
 'Leon': 0.0196078431372549,
 'Guy': 0.0196078431372549,
 'Louis': 0.0196078431372549,
 'Mike': 0.0196078431372549,
 'Ally': 0.0196078431372549,
 'Holly': 0.0196078431372549,
 'Pankaj': 0.0196078431372549,
 'Sravan': 0.0196078431372549,
 'Matthew': 0.0196078431372549,
 'Vanessa': 0.0196078431372549,
 'Gordon': 0.0196078431372549,
 'Di': 0.0196078431372549,
 'Siva': 0.0196078431372549,
 'Mel': 0.0196078431372549,
 'Allen': 0.0196078431372549,
 'Vinay': 0.0196078431372549,
 'Michelle': 0.0196078431372549,
 'Jess': 0.0196078431372549,
 'Cindy': 0.0196078431372549,
 'Kirsten': 0.0196078431372549,
 'Mirza': 0.0196078431372549,
 'Umair': 0.0196078431372549}
