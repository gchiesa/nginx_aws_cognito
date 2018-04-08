# NGINX Config


```
location /private/ {
    auth_request /auth;
    auth_request_set $cognito_username $upstream_http_x_aws_cognito_username;
    auth_request_set $cognito_accesstoken $upstream_http_x_aws_cognito_accesstoken;
    auth_request_set $cognito_attributesjson $upstream_http_x_aws_cognito_attributesjson;
    proxy_set_header X-AWS-Cognito-Username $cognito_username;
    proxy_set_header X-AWS-Cognito-AccessToken $cognito_accesstoken;
    proxy_set_header X-AWS-Cognito-AttributesJson $cognito_attributesjson;    
}

location = /auth {
    proxy_pass http://127.0.0.1:9988;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-AWS-Cognito-BasicAuth $http_authorization;
}
```
