from database import init_db, db_session
from datetime import datetime
from models import *

class Twitter:
    def __init__(self):
        self.currentUser = None
    """
    The menu to print once a user has logged in
    """
    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        #This function should register a new user for ATCS Twitter by prompting them to enter a username and password
        repeat = True
        while repeat:
            username = input("What will your Twitter handle be? \n")
            password = input("Enter a password \n")
            passcheck = input("Re-enter your password \n")
            if password == passcheck:
                print("The passwords don't match. Try again.\n")
                #######CONTENT STANDARD: Queried from a single table (done many times in problem set)
                if db_session.query(User).where(User.username == username).count() == 0:
                    newUser = User(username = username, password = password)
                    db_session.add(newUser)
                    print("Welcome " + username + "!\n")
                    repeat = False
                    self.currentUser = db_session.query(User).where(User.username == username).first()
                    db_session.commit()
                else:
                    print("That username is already taken. Try again.\n")
                
            else:
                print("The passwords don't match. Try again.\n")
    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        #This function should log the user in so that any action they take from here is linked to their account.
        repeat = True
        while repeat:
            username = input("Username: ")
            password = input("\nPassword: ")
            ###CONTENT STANDARD: More advnaced Query (Select statements)
            if db_session.query(User).where((User.username == username) & (User.password == password)).first() != None:
                print("Welcome @" + username + "!")
                self.currentUser = db_session.query(User).where(User.username == username and User.password == password).first()
                repeat = False
            else:
                print("Invalid username or password")
    
    def logout(self):
        self.currentUser = None

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        #This function should provide the user with options on startup. They should be able to decide to login, register a new user, or exit the program.
        print("Welcome to ATCS Twitter!\nPlease select a menu option")
        choice = int(input("1: Login\n2: Register User\n0: Exit\n"))
        if choice == 2:
            self.register_user()
        elif choice == 1: 
            self.login()
        elif choice == 0:
            self.logout()

    def follow(self):
        #This function should allow the user to follow another user. If successful, the method should print “You are now following @<username>”
        request = input("Who would you like to follow? \n")
        x = db_session.query(User).where(User.username == request).first()
        if x in self.currentUser.following:
            print("You already follow " + request)
            
        else:
            db_session.add(Follower(follower_id = self.currentUser.username, following_id = request))
            db_session.commit()
            print("You are now following @" + request)
        


    def unfollow(self):
        #This function should allow the user to unfollow another user. If successful, the method should print “You are no longer following @<username>”
        request = input("Who would you like to follow? \n")
        x = db_session.query(Follower).where((Follower.follower_id == self.currentUser.username) & (Follower.following_id==request)).first()

        if x is not None:
            db_session.delete(x)
            db_session.commit()
            print("You are no longer following " + request)

        else:
            print("You dont follow " + request)
                
                

    def tweet(self):
        #This function allows a user to create a new tweet with tags. 
        body = input("What text would you like in your tweet? \n")
        tags = input ("What tags would you like to add? \n").split()
        list = []
        for tag in tags:
            newTag = Tag(content = tag)
            list.append(newTag)
            db_session.add(newTag)
            db_session.commit()
        newTweet = Tweet(content = body, timestamp = datetime.now(), username = self.currentUser.username)
        db_session.add(newTweet)
        db_session.commit()
        for tag in list:
            newtt = TweetTag(tweet_id = newTweet.id, tag_id = tag.id)
            db_session.add(newtt)
            db_session.commit()
        
    def view_my_tweets(self):
        #This function should print ALL of the current users tweets
        own = db_session.query(Tweet).where(Tweet.username == self.currentUser.username).all()
        self.print_tweets(own)

    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        #This function should print the 5 most recent tweets of the users that the current user follows.
        x = []
        for user in self.currentUser.following:
            x.append(user.username)
        content = db_session.query(Tweet).where(Tweet.username.in_(x)).order_by(Tweet.timestamp).limit(5).all()
        self.print_tweets(content)

    def search_by_user(self):
        #This function should prompt the user to enter a username then print all of that user’s tweets
        user = input("\nWhich user's tweets would you like to see? ")
        x = db_session.query(User).where(User.username==user).first()
        if x is None:
            print("User does not exist")
            return
        content = db_session.query(Tweet).where(Tweet.username == user).order_by(Tweet.timestamp).all()
        self.print_tweets(content)

    def search_by_tag(self):
        #This function should prompt the user to enter a tag and then print all of the tweets that have that tag.
        tag = input("\nWhat tag would you like to search by? ")
        x = db_session.query(Tag).where(Tag.content==tag).all()
        if x is None:
            print("No tweets exist with this tag")
            return
        taglist = []
        for y in tag:
            taglist.append(y.id)
            content = db_session.query(Tweet).where((Tweet.id == TweetTag.tweet_id) & (TweetTag.tag_id.in_(taglist))).all()
            self.print_tweets(content)
            

    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        #Modify the run function so that, once logged in, the user can continuously select from the following menu options provided to you in the print_menu function:
        init_db()

        print("Welcome to ATCS Twitter!")
        self.startup()

        x = True
        while x:
            self.print_menu()
            option = int(input(""))

            if option == 1:
                self.view_feed()

            elif option == 2:
                self.view_my_tweets()

            elif option == 3:
                self.search_by_tag()

            elif option == 4:
                self.search_by_user()

            elif option == 5:
                self.tweet()

            elif option == 6:
                self.follow()

            elif option == 7:
                self.unfollow()

            else:
                self.logout()
                x = False
        self.end()
