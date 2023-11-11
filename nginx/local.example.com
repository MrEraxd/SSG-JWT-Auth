# If you want to check for specifcic value inside claim you
# can use map to do so use it like this
# map $jwt_claim_[name-of-claim] $[internal_variable_name] {
#   \"[value of this claim]\" 1
# }
# I will not use it as as default it expects any non 0 value
map $jwt_claim_p_orders_r $jwt_p_orders_r {
   \"1\" 1;
}

# This section will contains all info about server
server {
  # Port that server will listen on
  listen 80;

  # Root path that nginx will search files for
  root /var/www/html;

  # Setup redirection to allowed pages
  # based on error code
  error_page 401 =301 /login;
  error_page 403 =301 /;

  # Name of the domain that server will listen for me it is name of the file
  server_name local.example.com;

  # Key of the JWT check possible values in docs
  # https://github.com/max-lt/nginx-jwt-module/tree/15a170bf10208ecee74d9a22bf1058b36e6502aa
  auth_jwt_key "ultra_secret_key";
  
  # To enable JWT check for all locations under this server uncomment 
  # value below it is easier to disable check for few pages that don't
  # don't need it than adding it to every that needs we also have to tell
  # module that our cookie will be stored in cookie named AuthToken
  auth_jwt $cookie_AuthToken;

  # Path of api, because we are validating JWT on BE side 
  # there is no need to make additional validation here
  location /api {
    auth_jwt off;
    proxy_pass http://localhost:8000;
  }

  # Location where nuxt stores all transpiled files we also have to let
  # unauthorized users open this folder as they have to open login form.
  location /_nuxt {
    auth_jwt off;
  }

  # Now we have to define locations for requests
  # Location below will be responsible for opening /login path
  # in this example it will be local.example.com/login
  # this path wont be protected by JWT as we want our user to be able to login
  # so we will just return file responsible for that path
  location /login {
    auth_jwt off;
    try_files $uri $uri/ =404;
  }

  # Path / just requiers valid JWT to be present
  location / {
    try_files $uri $uri/ =404;
  }

  # Path /orders will require JWT to contain claim named
  # orders_r to open such path to do so just add
  # auth_jwt_require $[name_of_variable(s)]
  location /orders {
    auth_jwt_require $jwt_claim_p_orders_r;
    try_files $uri $uri/ =404;
  }
}