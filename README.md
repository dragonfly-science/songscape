kiwi-calls
==========

Application for displaying kiwi calls


## Development setup

For the best results use nginx to serve the media files during development. To do this on ubuntu 12.04

- install the latest nginx, add the following to `/etc/apt/sources.list.d/nginx.list`
```  
    deb http://nginx.org/packages/ubuntu/ precise nginx
    deb-src http://nginx.org/packages/ubuntu/ precise nginx
```

- run
```
    wget -qO - http://nginx.org/keys/nginx_signing.key | sudo apt-key add -
    apt-get update
    apt-get install nginx
```    

- something similar to /etc/nginx/conf.d/default.conf
```
    server {
        listen   80;  # or say 9000 if you want to run apache
        server_name foo.dragonfly.co.nz;
        # no security problem here, since / is alway passed to upstream
        # serve directly - analogous for static/staticfiles
	    location /media/sonograms/ {
	        alias /kiwi/sonograms/;
	        expires 30d;
	    }
	    location /media/snippets/ {
	        alias /kiwi/snippets/;
	        expires 30d;
	    }
        location /media/ {
    	    alias /home/foo/dragonfly/songscape/media/;
    	    expires 30d;
        }
        location /static/ {
    	    alias /home/foo/dragonfly/songscape/static/;
    	    expires 30d;
        }
        location / {
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_connect_timeout 10;
            proxy_read_timeout 10;
            proxy_pass http://localhost:8000/;
        }
        # what to serve if upstream is not available or crashes
        error_page 500 502 503 504 /media/50x.html;
    }
```
