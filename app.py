import bot
option = 0
print("Please login:")
username = input()
password = input()
tweetBot = bot.Twitter(username,password)
while(option > -1):
    try:
        exit = int(input("1. Follow user\n2. Like Tweet\n3. Comment\n4. Retweet\n5. Get feed\n6. Get User's Feed\n7. Search feed\n0. Logout\n"))
    except:
        print("Invalid option")
    if exit < 8 and exit > -1:
        if exit == 0:
            print("Logging out")
            tweetBot.dispose()
            break
        elif exit == 1:
            tweetBot.followUser(input())
        elif exit == 2:
            tweetBot.likeArticle(input())
        elif exit == 3:
            tweetBot.commentArticle(input(),input())
        elif exit == 4:
            tweetBot.retweetArticle(input())
        elif exit == 5:
           tweetBot.getFeed()
        elif exit == 6:
           tweetBot.getUserFeed(input())
        elif exit == 7:
           tweetBot.getSearchFeed(input())
           
    else:
        print("Invalid option")