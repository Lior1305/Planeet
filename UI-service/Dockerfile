# Use nginx alpine for lightweight image
FROM nginx:alpine

# Copy your HTML and assets to nginx's default serving directory
COPY . /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# nginx will start automatically
CMD ["nginx", "-g", "daemon off;"]