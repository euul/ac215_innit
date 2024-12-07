FROM node:16

WORKDIR /app

# Copy package.json and install dependencies
COPY src/package.json ./
RUN npm install

# Copy the rest of the files
COPY src/ ./src/
COPY public/ ./public/

CMD ["npm", "start"]
