# Affluena Contribution System Web App

Before you can contribute and make use of this web app, either the customer management system or the full application, you need to have at least deployed an django application before and have at least an intermidate knowledge of Django.
- For Customer Management Side
  You need an intermediate knowledge  of django
- For the full web app
  You need at least an intermediate knowledge of Django, Django-Rest-Framework

## Backend development workflow

- Install the requirements from the requirements.txt
  with pip install -r requirements.txt
- Connect your database
    currently using PostgreSQL database
- Run Migrations
- Create Super User
- Create Group named Staff

## Functionalities 

  ```
  - Users can register and Login
  - Create Order (Make Payments - either Compound or Simple)
  - Generate Receipt on Confirmation 
  - Email Notification to admin on Order
  - Referral System
  - Custom Admin Dashboard different from django admin

  ```

###### Authentication Rest Endpoints 
  ```
  - Normal Login Endpoint - http://127.0.0.1:8000/rest-auth/login/
  - Register Endpoint - http://127.0.0.1:8000/rest-auth/registration/
  - Confim Email - http://127.0.0.1:8000/account-confirm-email/
  - Forgot Password - http://127.0.0.1:8000/password/reset/
  - Reset Password - http://127.0.0.1:8000/rest-auth/password/reset/confirm/
  - Resend Verification Email - http://127.0.0.1:8000/resend-verification-email/

  ```




