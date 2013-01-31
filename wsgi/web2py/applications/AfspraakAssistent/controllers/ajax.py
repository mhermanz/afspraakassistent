import datetime
import locale

@auth.requires_login()
def saveintro():
    html = request.vars['html']
    db(db.auth_user.id == auth.user.id).update(description=html)
    
@auth.requires_login()
def addafspraaktype():  
    afspraaktype = request.vars['afspraaktype']
    db.afspraaktype.insert(auth_user_id=auth.user.id,naam=afspraaktype,lengte=60,prijs=0)
    return afspraaktype
    
@auth.requires_login()
def removeafspraaktype():  
    afspraakid = request.vars['afspraakid']
    db(db.afspraaktype.id == afspraakid).delete()
    
@auth.requires_login()
def editafspraaktype(): 
    afspraakid = request.vars['afspraakid']
    rows = db(db.afspraaktype.id == afspraakid).select(db.afspraaktype.ALL)
    return dict(afspraak=rows[0])
    
@auth.requires_login()
def saveafspraaktype(): 
    afspraakid = request.vars['afspraakid']
    lengte = request.vars['lengte']
    naam = request.vars['naam']
    rows = db(db.afspraaktype.id == afspraakid).update(naam = naam,lengte = lengte)
    return ""
     
def saveklant(): 
    email = request.vars['email']
    naam = request.vars['naam']
    telefoon = request.vars['telefoon']
    straat = request.vars['straat']
    huisnummer = request.vars['huisnummer']
    postcode = request.vars['postcode']
    plaats = request.vars['plaats']
    db.klant.insert(email=email,naam=naam,telefoon=telefoon,straat=straat,huisnummer=huisnummer,postcode=postcode,plaats=plaats);
    return True
    
def boekafspraak():
    klantid = request.vars['klantid']
    userid = request.vars['userid']
    afspraaktypeid = request.vars['afspraaktypeid']
    afspraaktijdstipid = request.vars['afspraaktijdstipid']
    email = request.vars['email']
    
    if (db((db.afspraaktijdstip.id == afspraaktijdstipid) & (db.afspraaktijdstip.enabled == True)).count() == 0):
        return False
    
    if (db((db.klant.id == klantid) & (db.klant.email == email)).count() == 0): #email klopt niet met klantid
        return False
        
    db(db.afspraaktijdstip.id == afspraaktijdstipid).update(enabled = False);
    
    afspraaktijdstip = db(db.afspraaktijdstip.id == afspraaktijdstipid).select(db.afspraaktijdstip.ALL)[0]
    afspraaktype = db(db.afspraaktype.id == afspraaktypeid).select(db.afspraaktype.ALL)[0]
    
    #hier zometeen alle onderliggende tijdstippen disabelen
    
    db.afspraak.insert(afspraaktype_id=afspraaktypeid,klant_id=klantid,datum=afspraaktijdstip.datum,tijd=afspraaktijdstip.tijd,lengte=afspraaktype.lengte, prijs=afspraaktype.prijs,naam=afspraaktype.naam)
    
    user = db(db.auth_user.id == userid).select(db.auth_user.ALL)[0]
    klant = db(db.klant.id == klantid).select(db.klant.ALL)[0]
    
    mail.send(to=[klant.email],
          subject='Afspraak met ' + user.sitename,
          reply_to=user.email,
          message='U heeft een afspraak gemaakt.')
    
    mail.send(to=[user.email],
          subject='Afspraak met ' + klant.naam,
          reply_to=klant.email,
          message='Er is een afspraak ingeboekt.')
    
    return True
    
@auth.requires_login()
def loadafspraaktype():  
    return dict(afspraaktypen=db(db.afspraaktype.auth_user_id == auth.user.id ).select(db.afspraaktype.ALL))
    
@auth.requires_login()
def addtijd():  
    dt = datetime.datetime.strptime(request.vars['tijd'], "%Y-%m-%dT%H:%M")
    afspraaktypeid = request.vars['afspraaktypeid']
    d = dt.date()
    t = datetime.time(dt.hour,dt.minute)
    db((db.afspraaktijdstip.afspraaktype_id==afspraaktypeid) & 
        (db.afspraaktijdstip.datum==d) & 
        (db.afspraaktijdstip.tijd==t) & 
        (db.afspraaktijdstip.enabled==True)).delete()
    db.afspraaktijdstip.insert(afspraaktype_id=afspraaktypeid,datum=d,tijd=t,enabled=True)
    return 'OK'
    
@auth.requires_login()
def deletetijd():  
    dt = datetime.datetime.strptime(request.vars['tijd'], "%Y-%m-%dT%H:%M")
    afspraaktypeid = request.vars['afspraaktypeid']
    d = dt.date()
    t = datetime.time(dt.hour,dt.minute)
    db((db.afspraaktijdstip.afspraaktype_id==afspraaktypeid) & 
        (db.afspraaktijdstip.datum==d) & 
        (db.afspraaktijdstip.tijd==t) & 
        (db.afspraaktijdstip.enabled==True)).delete()
    return 'OK'
    
@auth.requires_login()
def loadtijden():
    ddd = request.vars['datum']
    date = datetime.datetime.strptime(ddd, "%Y-%m-%d").date()
    #date = datetime.datetime.now().date()
    dates = []
    locale.setlocale(locale.LC_ALL, '')
    for day in range(0,1):
        dateitem = (date + datetime.timedelta(days=day),[])
        dates.append(dateitem)
        for atype in db(db.afspraaktype.auth_user_id == auth.user.id).select(db.afspraaktype.ALL):
            
            items = db((db.afspraaktijdstip.afspraaktype_id==atype.id) & 
                (db.afspraaktijdstip.datum==dateitem[0])).select(db.afspraaktijdstip.ALL,
                orderby=db.afspraaktijdstip.tijd).as_list(storage_to_dict=False)
            
            afspraakitem = (atype,[])
            dateitem[1].append(afspraakitem)
            for num in range(0,96):
                timeitem = [datetime.time(num/4, (num%4)*15),False]
                if (len(items) > 0 and items[0].tijd == timeitem[0]):
                    timeitem[1] = True
                    items.pop(0)
                afspraakitem[1].append(timeitem)
    return dict(items=dates,datum=ddd)
