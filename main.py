
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images
from google.appengine.api import urlfetch

# ORM models

class ResizedImage(db.Model):
  url = db.StringProperty(multiline=False)
  image = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)

# handlers 

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('ooh-la-la, webapps!')

class ImgResize(webapp.RequestHandler):
  def get(self):

#	fetchurl with alt header?   	
#    ua_string = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1) Gecko/20090624 Firefox/3.5"
#	,headers={'User-Agent': ua_string}

    img_url = self.request.get('i')
    width = 400
    height = 400
	  
    if self.request.get('w'):
      width = int(self.request.get('w'))
	  
    if self.request.get('h'):
      height = int(self.request.get('h'))
      
    img = self.getFromDataStore(img_url)
    
    if not (img and img.image):
    	img = ResizedImage()
    	img.url = img_url
    	img.image = db.Blob(urlfetch.Fetch(img_url).content) # ,headers = {'User-Agent': "Mozilla/5.0"},allow_truncated=True 
    	img.put()
    
    try:
      self.image = images.resize(img.image,width,height)	    
      self.response.headers['Content-Type'] = 'image/jpeg'
      self.response.out.write(self.image)
    except:
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write(img_url + " is not an image?")  
      # TODO _ show response headers ??	
    
  
  def getFromDataStore(self,url):
    result = db.GqlQuery("SELECT * FROM ResizedImage WHERE url = :1 LIMIT 1", url).fetch(1)
    if (len(result) > 0):
      return result[0]
    else:
      return None

class GetUrl(webapp.RequestHandler):
  def get(self):
    url = self.request.get('u')
    response = urlfetch.Fetch(url,headers={'User-Agent': "Mozilla/5.0 "}).content
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(response)



application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/img', ImgResize),
  ('/url', GetUrl)
  ],debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()