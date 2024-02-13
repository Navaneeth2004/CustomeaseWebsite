from flask import Flask,render_template,request,url_for,redirect,session, flash, jsonify
import mysql.connector
from datetime import timedelta

mydbms = mysql.connector.connect(host="sql6.freesqldatabase.com", user="sql6682381", passwd="aBaW5bh5hF", database="sql6682381",)

cur = mydbms.cursor()

#############################################################################################
class functions():

    tableinsert=0
    resultname=""
    resulttable=""

    def get_action(self):

        select_action = f"SELECT response from action_info_{session['botname']} WHERE trig=%s"
        select_table = f"SELECT * FROM table_info_{session['botname']}"
        select_action_names = f"SELECT trig FROM action_info_{session['botname']}"
        select_table_names = f"SELECT name FROM table_info_{session['botname']}"

        text = session["currentmsg"].replace("\n","").rstrip()

        print("this is what i got "+text)

        if text.startswith('%') and text.endswith('%'):
            print("if workedd")
            try:
                cur.execute(select_table)
                existing_userpass = cur.fetchall()
                userpassresult = False

                for i in existing_userpass:
                    if i[0] == text.replace("%",""):
                        self.resultname = i[0]
                        self.resulttable = i[2]
                        resultaddi = i[3]
                        userpassresult = True
                        self.tableinsert=1
                        ask = f"""form = {self.resulttable}\n\n{resultaddi}"""
                        return ask
   
                if(userpassresult == False):
                    return "No Form was found"
                    
            except:
                print("SQL Error")

        elif(self.tableinsert==1):
            print("entered insertion")
            try:
                values = text.split(',')
                formatted_values = ','.join([f"'{val.strip()}'" for val in values])
                
                select_filler = f"INSERT INTO data_{self.resultname} (user,{self.resulttable}) VALUES ('{session['username']}',{formatted_values})"
                print(select_filler)
                cur.execute(select_filler)
                mydbms.commit()
                self.tableinsert=0
                return "Form filled Successfully"
            except Exception as e:
                print(e)
                self.tableinsert=0
                return "Fill the form correctly"

        elif text.lower() == "!action!":
            try:
                cur.execute(select_action_names)
                existing_userpass = cur.fetchall()

                if(existing_userpass == None):
                    return "No actions available"
                else:
                    formatted = "\n".join([str(item[0]) for item in existing_userpass])
                    return "Trigger commands:\n"+formatted
            except Exception as e:
                print(e)

        elif text.lower() == "!form!":
            try:
                cur.execute(select_table_names)
                existing_userpass = cur.fetchall()

                if(existing_userpass == None):
                    return "No actions available"
                else:
                    formatted = "\n".join([str(item[0]) for item in existing_userpass])
                    return "Form commands:\n"+formatted
            except Exception as e:
                print(e)

        elif(self.tableinsert==0):
            print("else worked")
            try:
                cur.execute(select_action,(text,))
                existing_userpass = cur.fetchone()

                if(existing_userpass is not None):
                    return existing_userpass[0]
                else:
                    pass
            except:
                print("SQL error")
        print(self.tableinsert)

##############################################################################################

check_names_table = "SELECT username FROM signin_info WHERE username=%s"

app = Flask(__name__)
app.secret_key = "qpwoeialskdjzmxnvb"
app.permanent_session_lifetime = timedelta(hours=5)

if __name__ == "__main__":
    functions_instance = functions()

#############################################################################################
@app.route("/", methods=["POST","GET"])
def home():
    if request.method == "POST":

        botname = request.form["botname"]
        username = request.form["username"]

        try:
            cur.execute(check_names_table,(botname,))
            existing_userpass = cur.fetchone()

            if(botname.strip()=="" or username.strip()==""):
                flash("Cannot leave any fields blank", "error")
            elif(existing_userpass is None):
                flash("Botname was not found", "error")
            
            else:
                session["botname"] = botname
                session["username"] = username
                return redirect(url_for("chat_home"))
        except Exception as e:
            print(e)
            return "<script>alert('Error Encountered..')</script>"

    return render_template("nochat.html")

#############################################################################################

@app.route("/chatbot/", methods=["POST", "GET"])
def chat_home():
    if "username" in session:
        username = session["username"]
        botname = session["botname"]

        text = None

        if request.method == "POST":
            session["currentmsg"] = request.form.get("text")
            text = functions_instance.get_action()

            return jsonify({"botchat": text})
            
    
        return render_template("chat.html", chatbotname=botname)
    
    else:
        return redirect(url_for("home"))

#############################################################################################
    
@app.route("/clear_currentmsg", methods=["GET"])
def clear_currentmsg():
    session.pop("currentmsg", None)
    return "Currentmsg cleared!"
    
app.run(debug=True)

