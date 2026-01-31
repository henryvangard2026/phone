from flask import Flask, render_template, request, redirect, url_for, flash
import phone as ph


#
#  STATUS:  completed
#


howtorun = r'''

#
# HOWTO:
# 
# flask --app flaskphone --debug run
#
# run it then go to:  http://127.0.0.1:5000 or http://localhost:5000
#
# ENDPOINTS:
#
# 1.  view all phones, home (/):  http://localhost:5000/
#
# 2.  view one phone ID:  http://localhost:5000/phone_id
#
# 3.  update one phone:  http://localhost:5000/update/phone_id
#
# 4.  add a phone:  http://localhost:5000/add
#

'''


app = Flask(__name__)
app.secret_key = "devkey"   # required for flash messages


# get a DB session
# ################################################

def get_db():
    session = ph.Session()
    try:
        yield session
    finally:
        session.close()


# / for home:  view all phones
# ################################################

@app.route("/")
def index():
    session = ph.Session()
    phones = session.query(ph.Phone).all()
    session.close()
    return render_template("index.html", phones=phones)


# view one phone
# ################################################

@app.route("/phone/<int:phone_id>")
def view_phone(phone_id):
    session = ph.Session()
    phone = session.query(ph.Phone).filter_by(id=phone_id).first()
    session.close()

    if not phone:
        flash(f"Phone ID {phone_id} not found")
        return redirect(url_for("index"))

    return render_template("view_phone.html", phone=phone)


# add a phone
# ################################################

@app.route("/add", methods=["GET", "POST"])
def add_phone():
    if request.method == "POST":
        session = ph.Session()
        
        try:
            phone = ph.Phone(
                brand=request.form["brand"].upper(),
                model=request.form["model"].upper(),
                os=request.form["os"].upper(),
                os_version=request.form["os_version"],
                serial_number=request.form["serial_number"].upper(),
                imei=request.form["imei"].upper(),
                status=request.form["status"].upper(),
                workstation=request.form["workstation"].upper()
            )

            ph.capPhoneDetails(phone)
            session.add(phone)
            session.commit()

            flash("Phone added successfully")
            return redirect(url_for("index"))

        except Exception as e:
            session.rollback()
            flash(f"Error adding phone: {e}")

        finally:
            session.close()

    return render_template("add_phone.html")


# update a phone
# ################################################

@app.route("/update/<int:phone_id>", methods=["GET", "POST"])
def update_phone(phone_id):
    session = ph.Session()
    phone = session.query(ph.Phone).filter_by(id=phone_id).first()

    if not phone:
        session.close()
        flash(f"Phone ID {phone_id} not found")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            phone.brand = request.form["brand"].upper()
            phone.model = request.form["model"].upper()
            phone.os = request.form["os"].upper()
            phone.os_version = request.form["os_version"]
            phone.serial_number = request.form["serial_number"].upper()
            phone.imei = request.form["imei"].upper()
            phone.status = request.form["status"].upper()
            phone.workstation = request.form["workstation"].upper()

            session.commit()
            flash("Phone updated successfully")
            return redirect(url_for("view_phone", phone_id=phone.id))

        except Exception as e:
            session.rollback()
            flash(f"Error updating phone: {e}")

        finally:
            session.close()

    session.close()
    return render_template("update_phone.html", phone=phone)


# delete a phone
# ################################################

@app.route("/delete/<int:phone_id>", methods=["POST"])
def delete_phone(phone_id):
    session = ph.Session()
    phone = session.query(ph.Phone).filter_by(id=phone_id).first()

    if not phone:
        session.close()
        flash(f"Phone ID {phone_id} not found")
        return redirect(url_for("index"))

    try:
        session.delete(phone)
        session.commit()
        flash("Phone deleted successfully")

    except Exception as e:
        session.rollback()
        flash(f"Error deleting phone: {e}")

    finally:
        session.close()

    return redirect(url_for("index"))


# main:  run Flask
# ################################################

if __name__ == "__main__":
    app.run(debug=True)
