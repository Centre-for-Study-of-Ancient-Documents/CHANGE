# Use an official Nginx image as the base
FROM nginx:alpine

# Remove the default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy static files from the current directory to Nginx's default directory
COPY ./public /usr/share/nginx/html

# Expose port 80 for HTTP traffic
EXPOSE 80