from flask import Flask, render_template, url_for, flash, request, redirect, jsonify
from flask_mysql_connector import MySQL
import shortuuid

# Inicializamos variables
app = Flask(__name__)

# Endpoint
endpoint = "http://shorty.url"

# MySQL Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DATABASE'] = 'db_short_urls'

# Inicializating MySQL
mysql =  MySQL(app)

# Private key to use flash messages
app.secret_key = "C1av353cr3t4"   
        

# Initial route
@app.route('/', methods=['GET'])
def inicio():
    try:
        return render_template('index.html'),200
    except:
        return render_template('404.html'),404

# Route to create short link and store it in the database
@app.route('/create_short_link', methods=['POST'])
def create_short_link():
    try:
        if request.method == 'POST':
            # Catch url
            url = request.form['url']
            if not url:
                flash("URL is missing", "error")
                return redirect(url_for('inicio'))
            cursor = mysql.connection.cursor()
            
            # Validate short link
            while True:
                
                # Generate the short link
                short_link = shortuuid.ShortUUID().random(length=7)
                # Consultate into database if exists a same link
                cursor.execute(
                    "SELECT * FROM LINKS WHERE SHORT_LINK = BINARY %s", (short_link,))
                
                if not cursor.fetchone():
                    break
            
            # Consult if exists URL into database
            cursor.execute("SELECT SHORT_LINK FROM LINKS WHERE URL = BINARY %s", (url,))
            data = cursor.fetchone()
            if data:
                flash(endpoint + '/' + data[0])
                return redirect(url_for('inicio')), 302
                
            # We enter the requested url into the database
            cursor.execute(
                "INSERT INTO links (url, short_link) VALUES (%s, %s)", (url, short_link))
            
            # Save changes in database
            mysql.connection.commit()
            
            # Close the connection in database
            cursor.close()
            new_link = endpoint + '/' + short_link
            flash(new_link)
            return redirect(url_for('inicio')), 302
    except:
        return render_template('404.html'), 404



# Route to go to URL from database
@app.route('/<id>')
def get_url(id):
    try:
        cursor = mysql.connection.cursor()
        
        # Search in database the address
        cursor.execute("SELECT URL FROM LINKS WHERE SHORT_LINK = BINARY %s", (id,))
        
        # Save in a variable
        data = cursor.fetchone()
        
        # Close connection from database
        cursor.close()
        return render_template('ads.html', url=data[0]), 200
    except:
        return render_template('404.html'), 404
    

# Running app
if __name__ == "__main__":
    app.run(port=80, debug=True)
