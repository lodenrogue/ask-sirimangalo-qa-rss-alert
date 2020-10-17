Create a file named env.env and add sender email address and password properties:

```
EMAIL_ADDRESS=${YOUR_EMAIL}
EMAIL_PASS=${YOUR_PASSWORD}
```

Create a file named email_list and add email addresses, 1 per line, for intended recipients:

```
example@example.com
another@example.com
```

To build and run application run:

```
docker build -t message-alert .
docker run --env-file env.env message-alert
```

