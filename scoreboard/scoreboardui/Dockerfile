# Use Node.js image
FROM node:16

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm install

# Copy the project files
COPY . .

# Expose the port and build the app
EXPOSE 3000
CMD ["npm", "start"]
