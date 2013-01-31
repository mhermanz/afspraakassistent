routes_in = [
  ('/admin', '/welcome'),
  ('/admin/$anything', '/admin/$anything'),
  ('/AfspraakAssistent/$anything', '/AfspraakAssistent/$anything'),
  ('/login', '/AfspraakAssistent/default/user/login'),
  ('/', '/AfspraakAssistent/default/index'),
  ('/$anything', '/AfspraakAssistent/default/usersite/$anything')
]


routes_out = [
  ('/AfspraakAssistent/default/usersite/$anything','/$anything'),
  ('/AfspraakAssistent/default/user/login','/login'),
  ('/AfspraakAssistent/default/index','/')
]