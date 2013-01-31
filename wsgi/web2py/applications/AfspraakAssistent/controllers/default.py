# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import datetime

def index():
    return dict()
    
def contact():
    return dict()
    
@auth.requires_login()
def mijnafspraakassistent():
    user = db(db.auth_user.id == auth.user.id ).select(db.auth_user.ALL)[0]
    return dict(intro=user.description,site=URL('usersite',args=[user.sitename],scheme=True, host=True))
   
def email():
    afspraaktypeid = request.vars['at']
    afspraaktijdstipid = request.vars['ats']
    userid = request.vars['uid']
    return dict(afspraaktypeid=afspraaktypeid,afspraaktijdstipid=afspraaktijdstipid,userid=userid)
   
def boek():
    afspraaktypeid = request.vars['at']
    afspraaktijdstipid = request.vars['ats']
    userid = request.vars['uid']
    email = request.vars['email']
    
    rows = db(db.klant.email == email).select(db.klant.ALL)
    if (len(rows) == 0):
        redirect(URL('klant', vars={'uid':userid,'at':afspraaktypeid,'ats':afspraaktijdstipid,'email':email}))
        
    user = db(db.auth_user.id == userid).select(db.auth_user.ALL)[0]
    afspraaktype = db(db.afspraaktype.id == afspraaktypeid).select(db.afspraaktype.ALL)[0]
    afspraaktijdstip = db(db.afspraaktijdstip.id == afspraaktijdstipid).select(db.afspraaktijdstip.ALL)[0]
    
    wanneer = afspraaktijdstip.datum.strftime("%A %d %B %Y") + "  " + afspraaktijdstip.tijd.strftime("%H:%M")
    
    urlerror = URL('boekingsfout', vars={'uid':userid,'at':afspraaktypeid,'ats':afspraaktijdstipid})
    urlok = URL('boekinggelukt', vars={'uid':userid,'at':afspraaktypeid,'ats':afspraaktijdstipid})
    
    return dict(klantid=rows[0].id,afspraaktypeid=afspraaktypeid,afspraaktijdstipid=afspraaktijdstipid,userid=userid,email=email,waar=user.sitename,afspraaktype=afspraaktype.naam,wanneer=wanneer,urlerror=urlerror,urlok=urlok)
    
def boekinggelukt():
    afspraaktypeid = request.vars['at']
    afspraaktijdstipid = request.vars['ats']
    userid = request.vars['uid']
    user = db(db.auth_user.id == userid).select(db.auth_user.ALL)[0]
    afspraaktype = db(db.afspraaktype.id == afspraaktypeid).select(db.afspraaktype.ALL)[0]
    afspraaktijdstip = db(db.afspraaktijdstip.id == afspraaktijdstipid).select(db.afspraaktijdstip.ALL)[0]
    wat = afspraaktype.naam
    waar = user.sitename
    wanneer = afspraaktijdstip.datum.strftime("%A %d %B %Y") + "  " + afspraaktijdstip.tijd.strftime("%H:%M")
    url = URL('usersite',args=[user.sitename])
    return dict(wat=wat,waar=waar,wanneer=wanneer,url=url);
    
def boekingsfout():
    afspraaktypeid = request.vars['at']
    afspraaktijdstipid = request.vars['ats']
    userid = request.vars['uid']
    user = db(db.auth_user.id == userid).select(db.auth_user.ALL)[0]
    afspraaktype = db(db.afspraaktype.id == afspraaktypeid).select(db.afspraaktype.ALL)[0]
    afspraaktijdstip = db(db.afspraaktijdstip.id == afspraaktijdstipid).select(db.afspraaktijdstip.ALL)[0]
    wat = afspraaktype.naam
    waar = user.sitename
    wanneer = afspraaktijdstip.datum.strftime("%A %d %B %Y") + "  " + afspraaktijdstip.tijd.strftime("%H:%M")
    url = URL('usersite',args=[user.sitename])
    return dict(wat=wat,waar=waar,wanneer=wanneer,url=url);
    
def klant():
    afspraaktypeid = request.vars['at']
    afspraaktijdstipid = request.vars['ats']
    userid = request.vars['uid']
    email = request.vars['email']
    url = URL('boek',vars={'uid':userid,'at':afspraaktypeid,'ats':afspraaktijdstipid,'email':email})
    return dict(url=url,email=email)
    
def usersite():
    user = db(db.auth_user.sitename == request.args[0]).select(db.auth_user.ALL)[0]
    afspraken = db((db.afspraaktype.auth_user_id == user.id) & (db.afspraaktijdstip.afspraaktype_id == db.afspraaktype.id) & (db.afspraaktijdstip.datum >= datetime.datetime.now().date()) & (db.afspraaktijdstip.enabled==True)).select(db.afspraaktype.ALL,db.afspraaktijdstip.ALL,orderby=db.afspraaktijdstip.datum|db.afspraaktype.naam|db.afspraaktijdstip.tijd)
    
    curDateItem = (None,None)
    curTypeItem = (None,None)
    listdatum = []
    for afspraak in afspraken:
        if afspraak.afspraaktijdstip.datum <> curDateItem[0]:
            curDateItem = (afspraak.afspraaktijdstip.datum,[])
            curTypeItem =  (None,None)
            listdatum.append(curDateItem) 
        if afspraak.afspraaktype.naam <> curTypeItem[0]:
            curTypeItem = (afspraak.afspraaktype.naam,[])
            curDateItem[1].append(curTypeItem)
        curTypeItem[1].append(afspraak);
    
    return dict(intro=user.description,datums=listdatum,userid=user.id)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    
    field = db.auth_user['description']
    field.readable = field.writable = False
    
    return dict(form=auth())


@auth.requires_login()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


@auth.requires_login()
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
