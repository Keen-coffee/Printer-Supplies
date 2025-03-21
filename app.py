from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from pysnmp.hlapi import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toners.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Toner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family = db.Column(db.String(100), nullable=False)
    # Now stored as "b/w" or "color"
    color = db.Column(db.String(50), nullable=False)
    min = db.Column(db.Integer, nullable=False)
    # For b/w toners:
    black_inventory = db.Column(db.Integer, default=0)
    # For color toners:
    c_inventory = db.Column(db.Integer, default=0)
    m_inventory = db.Column(db.Integer, default=0)
    y_inventory = db.Column(db.Integer, default=0)
    k_inventory = db.Column(db.Integer, default=0)

class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'b/w' or 'color'
    toner_family = db.Column(db.String(100), nullable=True)
    page_count_oid = db.Column(db.String(100), default='1.3.6.1.2.1.43.10.2.1.4.1.1')
    c_oid = db.Column(db.String(100), default='1.3.6.1.2.1.43.11.1.1.9.1.2')
    m_oid = db.Column(db.String(100), default='1.3.6.1.2.1.43.11.1.1.9.1.3')
    y_oid = db.Column(db.String(100), default='1.3.6.1.2.1.43.11.1.1.9.1.4')
    k_oid = db.Column(db.String(100), default='1.3.6.1.2.1.43.11.1.1.9.1.1')
    # New fields for status
    page_count = db.Column(db.Integer, default=0)
    c_percentage = db.Column(db.Integer, default=0)
    m_percentage = db.Column(db.Integer, default=0)
    y_percentage = db.Column(db.Integer, default=0)
    k_percentage = db.Column(db.Integer, default=0)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    # Make the dashboard the home page.
    return redirect(url_for('dashboard'))

# ---------------- Toners routes --------------------

@app.route('/toners/setup', methods=['GET', 'POST'])
def toners_setup():
    if request.method == 'POST':
        family = request.form.get('family')
        toner_type = request.form.get('color')  # now a dropdown value: "b/w" or "color"
        min_value = request.form.get('min')
        if family and toner_type and min_value:
            if toner_type == "b/w":
                new_toner = Toner(
                    family=family,
                    color=toner_type,
                    min=int(min_value),
                    black_inventory=0
                )
            else:
                new_toner = Toner(
                    family=family,
                    color=toner_type,
                    min=int(min_value),
                    c_inventory=0,
                    m_inventory=0,
                    y_inventory=0,
                    k_inventory=0
                )
            db.session.add(new_toner)
            db.session.commit()
        return redirect(url_for('toners_setup'))
    toners = Toner.query.all()
    return render_template('toners_setup.html', toners=toners)

@app.route('/toners/delete/<int:toner_id>', methods=['POST'])
def delete_toner(toner_id):
    toner = Toner.query.get_or_404(toner_id)
    db.session.delete(toner)
    db.session.commit()
    return redirect(url_for('toners_setup'))

@app.route('/toners/edit/<int:toner_id>', methods=['GET', 'POST'])
def edit_toner(toner_id):
    toner = Toner.query.get_or_404(toner_id)
    if request.method == 'POST':
        toner.family = request.form.get('family')
        toner.color = request.form.get('color')
        toner.min = int(request.form.get('min'))
        db.session.commit()
        return redirect(url_for('toners_setup'))
    return render_template('edit_toner.html', toner=toner)

@app.route('/toners/list')
def toners_list():
    toners = Toner.query.all()
    return render_template('toners_list.html', toners=toners)

@app.route('/toners/increase/<int:toner_id>', methods=['POST'])
def increase_inventory(toner_id):
    toner = Toner.query.get_or_404(toner_id)
    toner.inventory += 1
    db.session.commit()
    return redirect(url_for('toners_list'))

@app.route('/toners/decrease/<int:toner_id>', methods=['POST'])
def decrease_inventory(toner_id):
    toner = Toner.query.get_or_404(toner_id)
    if toner.inventory > 0:
        toner.inventory -= 1
        db.session.commit()
    return redirect(url_for('toners_list'))

@app.route('/toners/increase/black/<int:toner_id>', methods=['POST'])
def increase_black(toner_id):
    toner = Toner.query.get_or_404(toner_id)
    toner.black_inventory += 1
    db.session.commit()
    return redirect(url_for('toners_list'))

@app.route('/toners/decrease/black/<int:toner_id>', methods=['POST'])
def decrease_black(toner_id):
    toner = Toner.query.get_or_404(toner_id)
    if toner.black_inventory > 0:
        toner.black_inventory -= 1
        db.session.commit()
    return redirect(url_for('toners_list'))

@app.route('/toners/increase/color/<int:toner_id>/<color>', methods=['POST'])
def increase_color(toner_id, color):
    toner = Toner.query.get_or_404(toner_id)
    if color == 'c':
        toner.c_inventory += 1
    elif color == 'y':
        toner.y_inventory += 1
    elif color == 'm':
        toner.m_inventory += 1
    elif color == 'k':
        toner.k_inventory += 1
    db.session.commit()
    return redirect(url_for('toners_list'))

@app.route('/toners/decrease/color/<int:toner_id>/<color>', methods=['POST'])
def decrease_color(toner_id, color):
    toner = Toner.query.get_or_404(toner_id)
    if color == 'c' and toner.c_inventory > 0:
        toner.c_inventory -= 1
    elif color == 'y' and toner.y_inventory > 0:
        toner.y_inventory -= 1
    elif color == 'm' and toner.m_inventory > 0:
        toner.m_inventory -= 1
    elif color == 'k' and toner.k_inventory > 0:
        toner.k_inventory -= 1
    db.session.commit()
    return redirect(url_for('toners_list'))

# ---------------- Printers routes --------------------

@app.route('/printers/setup', methods=['GET', 'POST'])
def printers_setup():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        ip_address = request.form.get('ip_address')
        printer_type = request.form.get('type')
        toner_family = request.form.get('toner_family')
        # OID fields from the form:
        page_count_oid = request.form.get('page_count_oid')
        # For b/w only:
        k_oid = ''
        # For color:
        c_oid = m_oid = y_oid = k_oid_color = ''
        if printer_type == 'b/w':
            k_oid = request.form.get('bw_k_oid')
        elif printer_type == 'color':
            c_oid = request.form.get('c_oid')
            m_oid = request.form.get('m_oid')
            y_oid = request.form.get('y_oid')
            k_oid = request.form.get('color_k_oid')
            
        new_printer = Printer(
            name=name,
            location=location,
            ip_address=ip_address,
            type=printer_type,
            toner_family=toner_family,
            page_count_oid=page_count_oid,
            c_oid=c_oid,
            m_oid=m_oid,
            y_oid=y_oid,
            k_oid=k_oid
        )
        db.session.add(new_printer)
        db.session.commit()
        return redirect(url_for('printers_setup'))

    # Retrieve distinct toner families for dropdown.
    toner_families = [family for (family,) in db.session.query(Toner.family).distinct().all()]
    printers = Printer.query.all()
    return render_template('printers_setup.html', printers=printers, toner_families=toner_families)

@app.route('/printers/delete/<int:printer_id>', methods=['POST'])
def delete_printer(printer_id):
    printer = Printer.query.get_or_404(printer_id)
    db.session.delete(printer)
    db.session.commit()
    return redirect(url_for('printers_setup'))

@app.route('/printers/edit/<int:printer_id>', methods=['GET', 'POST'])
def edit_printer(printer_id):
    printer = Printer.query.get_or_404(printer_id)
    # Retrieve distinct toner families for the dropdown.
    toner_families = [family for (family,) in db.session.query(Toner.family).distinct().all()]
    if request.method == 'POST':
        printer.name = request.form.get('name')
        printer.location = request.form.get('location')
        printer.ip_address = request.form.get('ip_address')
        printer.type = request.form.get('type')
        printer.toner_family = request.form.get('toner_family')
        db.session.commit()
        return redirect(url_for('printers_setup'))
    return render_template('edit_printer.html', printer=printer, toner_families=toner_families)

@app.route('/printers/list', methods=['GET'])
def printers_list():
    printers = Printer.query.all()
    return render_template('printers_list.html', printers=printers)

@app.route('/printers/update/<int:printer_id>', methods=['POST'])
def update_printer_status(printer_id):
    printer = Printer.query.get_or_404(printer_id)
    printer.page_count = int(request.form.get('page_count') or 0)
    printer.c_percentage = int(request.form.get('c_percentage') or 0)
    printer.m_percentage = int(request.form.get('m_percentage') or 0)
    printer.y_percentage = int(request.form.get('y_percentage') or 0)
    printer.k_percentage = int(request.form.get('k_percentage') or 0)
    db.session.commit()
    return redirect(url_for('printers_list'))

@app.route('/printers/refresh')
def refresh_printers():
    printers = Printer.query.all()
    for printer in printers:
        # SNMP GET for Page Count
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(
                SnmpEngine(),
                CommunityData('public'),
                UdpTransportTarget((printer.ip_address, 161), timeout=1, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(printer.page_count_oid))
            )
        )
        if errorIndication or errorStatus:
            printer.page_count = -1
        else:
            for varBind in varBinds:
                try:
                    printer.page_count = int(varBind[1])
                except:
                    printer.page_count = -1

        if printer.type == 'color':
            # For color printers, retrieve C, M, Y, K percentages
            for oid_field, attr in [(printer.c_oid, 'c_percentage'),
                                    (printer.m_oid, 'm_percentage'),
                                    (printer.y_oid, 'y_percentage'),
                                    (printer.k_oid, 'k_percentage')]:
                errorIndication, errorStatus, errorIndex, varBinds = next(
                    getCmd(
                        SnmpEngine(),
                        CommunityData('public'),
                        UdpTransportTarget((printer.ip_address, 161), timeout=1, retries=0),
                        ContextData(),
                        ObjectType(ObjectIdentity(oid_field))
                    )
                )
                if errorIndication or errorStatus:
                    setattr(printer, attr, -1)
                else:
                    for varBind in varBinds:
                        try:
                            setattr(printer, attr, int(varBind[1]))
                        except:
                            setattr(printer, attr, -1)
        else:
            # For B/W printers, update only K percentage
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(
                    SnmpEngine(),
                    CommunityData('public'),
                    UdpTransportTarget((printer.ip_address, 161), timeout=1, retries=0),
                    ContextData(),
                    ObjectType(ObjectIdentity(printer.k_oid))
                )
            )
            if errorIndication or errorStatus:
                printer.k_percentage = -1
            else:
                for varBind in varBinds:
                    try:
                        printer.k_percentage = int(varBind[1])
                    except:
                        printer.k_percentage = -1
    db.session.commit()
    return redirect(url_for('printers_list'))

@app.route('/dashboard')
def dashboard():
    low_toners = []
    for toner in Toner.query.all():
        if toner.color == 'b/w':
            # Show only if black_inventory is less than minimum.
            if toner.black_inventory < toner.min:
                low_toners.append(toner)
        else:
            # For color, check each inventory that is less than min.
            if (toner.c_inventory < toner.min or toner.m_inventory < toner.min or 
                toner.y_inventory < toner.min or toner.k_inventory < toner.min):
                low_toners.append(toner)

    low_printers = []
    for printer in Printer.query.all():
        if printer.type == 'b/w':
            if printer.k_percentage < 15:
                low_printers.append(printer)
        else:
            if (printer.c_percentage < 15 or printer.m_percentage < 15 or 
                printer.y_percentage < 15 or printer.k_percentage < 15):
                low_printers.append(printer)

    recommendations = []
    # Recommend ordering if toner inventory is exactly at the minimum and a printer is under 15%.
    for toner in Toner.query.all():
        if toner.color == 'b/w' and toner.black_inventory == toner.min:
            related = Printer.query.filter_by(toner_family=toner.family, type='b/w').all()
            for p in related:
                if p.k_percentage < 15:
                    recommendations.append(f"Order new toner for family {toner.family} (B/W)")
                    break
        elif toner.color == 'color':
            if (toner.c_inventory == toner.min or toner.m_inventory == toner.min or 
                toner.y_inventory == toner.min or toner.k_inventory == toner.min):
                related = Printer.query.filter_by(toner_family=toner.family, type='color').all()
                for p in related:
                    if (p.c_percentage < 15 or p.m_percentage < 15 or 
                        p.y_percentage < 15 or p.k_percentage < 15):
                        recommendations.append(f"Order new toner for family {toner.family} (Color)")
                        break

    return render_template('dashboard.html',
                           low_toners=low_toners,
                           low_printers=low_printers,
                           recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)