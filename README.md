<a href="https://zzhu805.pythonanywhere.com/">🌎View Live Site</a>

# Lincoln Fitness: Club Management System

This project delivers a Flask web app for Lincoln Fitness, a gym with more than 1,000 members and trainers. The app will assist gym staff with their daily activities and allows members to interact with Lincoln Fitness through a convenient interface.

**About the gym's operations**

- The gym charges a membership fee of $100 per month which is deducted by way of direct debit on the first of each month.
- All PT sessions are $50/hr and must be paid for by credit # Lincoln Fitness: Club Management System

This project delivers a Flask web app for Lincoln Fitness, a gym with more than 1,000 members and trainers. The app will assist gym staff with their daily activities and allows members to interact with Lincoln Fitness through a convenient interface.

**About the gym's operations**

- The gym charges a membership fee of $100 per month which is deducted by way of direct debit on the first of each month.
- All PT sessions are $50/hr and must be paid for by credit card at the time a session is booked.
- Classes are complimentary with every gym membership.
- Classes and PT sessions may be cancelled at any time before they occur. However, a member only receives a refund of their PT session fee if a cancellation is made 7 days prior to the session or earlier.

## Table of contents

1. [Layout of the app](#layout)
2. [Members Centre](#memberscentre)
3. [Manager's Centre](#managerscentre)
4. [Installation](#installation)

<a name="layout"></a>

## 1. Layout of the app

The gym's home page is accessible via the default route. A horizontal navigation bar and series of tiles featured on this page both allow visitors to navigate to pages where they may view:

- **Classes**: a class timetable displayed in a calendar format
- **PT Sessions**: personal training sessions can be viewed in a calendar format or filtered by trainer
- **Membership**: an explanation of membership and personal training fees.

![image](https://user-images.githubusercontent.com/100200726/226166356-741130c2-28a8-4839-88a7-501d35994b85.png)

All other functions of the app can only be accessed if a user logs in to the members, trainer or manager's centre as described below.

<a name="memberscentre"></a>

## 2. Members Centre

Gym members may login by clicking a link on the home page's horizontal navigation bar:

![home nav bar](https://user-images.githubusercontent.com/100200726/227762142-cb768d18-677f-45a0-bfea-7fa1b767ffc9.jpg)

A member logs in by entering their email address and password. A full list of members' email addresses and passwords is found in the 'member' table created by the SQL file in this repository. However, for ease of reference, the Members Centre can be accessed using:

**Email:** Zhiyi@gmail.com
**Password:** Zhiyi2023

Upon login, a member can access a dropdown menu in the top right hand corner of the screen:

![image](https://user-images.githubusercontent.com/100200726/228117179-b66a7b36-40b1-4521-953b-2c524612e11c.png)

This allows a member to select:

- **My Subscription**: the member can cancel or reactivate their auto-renewing membership subscription. A $100 monthly subscription fee is deducted by way of direct debit on the first of each month unless the member has cancelled it.
- **My Profile**: the member can view and edit their personal profile. They are also able to cancel their membership subscription via their profile.
- **My Bookings**: the member may view existing bookings for classes and PT sessions.
- **My Messages**: the member can review a summary of notifications they have received from the gym regarding payments and bookings. Weekly updates sent by the gym also appear on this page.
- **Reset Password**: the member may reset their password provided the new password has at least eight digits
- **Logout**: the member can log out of the Member Centre and will be redirected to the home page.

Once a member is logged in, they can navigate to 'Classes' or 'PT Sessions' on the horizontal navigation bar and select a class or PT session to book. The system will prevent a member from making a booking if they already have a booking at that time.

<a name="trainercentre"></a>


## 3. Manager's Centre

The gym's manager can login to the Manager's Centre via the _'/admin'_ route using the following details:

**User name:** manager
**Password:** administrator

### Navigation bar option: 'Dashboard'

This link returns the manager to the manager's dashboard. The dashboard features a number of tiles linking to features within the Manager's Centre:

![image](https://user-images.githubusercontent.com/100200726/228355493-c6e9337e-a9d1-407e-b39a-8e41951e3225.png)

### Navigation bar option: 'Members'

If 'Members' is expanded on the vertical navigation bar, the manager will have the option of navigating to:

- **Member List**: this is a list of all gym members. Inactive members are highlighted red. The manager can also filter by member type: active, inactive and archived (futher explanation of these terms is set out below). The manager can click 'view details' to view a member's personal profile. They can then choose whether to edit that profile.
- **Add a member**: the manager can add a new member to the gym's system.

_What is meant by an 'active', 'inactive' and 'archived' member?_

A member is active if they are a current member and their membership subscription payments are up to date.

An inactive member is one was has missed a subscription payment. They can login to the member centre, but cannot book any classes or PT sessions. If they pay subscriptions owing to the gym at the front desk, the manager can reinstate them as an 'active' member.

An 'archived' member is one who has cancelled their subscription and is unlikely to return to the gym. Such members are not deleted from the system, but they cannot log in. This status can be used to design reports where they will not feature. Their data is not archived in the technical sense of being moved and stored in another location.

### Navigation bar option: 'Trainers'

If 'Trainers' is expanded on the vertical navigation bar, the manager will have the option of navigating to:

- **Trainer List**: this is a list of the gym's trainers members. The manager can click 'view details' to view a trainers's personal profile. They can then choose whether to edit that profile. This includes specifying whether a trainer is active or archived (as described below).
- **Add a trainer**: the manager can add a new trainer to the gym's system
- **View Trainer Classes**: the manager can see the total number of classes a trainer has booked within a given date range, and elect to view the details of those classes.

_What is meant by an 'active' or 'archived' trainer?_

A trainer is active if they are a current employee of the gym.

An 'archived' trainer is one who is unlikely to return to the gym. Such trainers are not deleted from the system, but they cannot log in. This status can be used to design reports where they will not feature. Their data is not archived in the technical sense of being moved and stored in another location.

### Navigation bar option: 'Reports'

If 'Reports' is expanded on the vertical navigation bar, the manager will have the option of navigating to:

- **Financial Reports**: this page allows the manager to generate financial reports for a selected period. Revenue is broken down between membership and PT session revenue.
- **Class popularity report**: the manager can create a report showing the popularity of various class types during a selected time period
- **Member Attendance Report**: the manager can generate a report showing the total number of gym attendees during a selected period and the reason for their visit (PT session, class or general gym use).

### Navigation bar option: 'Member weekly update'

The manager can enter details for an update to be sent to members who are subscribing to notifications. This update will appear in a member's 'My messages' section. In addition, the system will automatically send monthly fee reminders to members via the 'myMessage' function outlined in app.py in this repository.

### Navigation bar option: 'Manager'

By clicking on 'manager', the manager has the option of logging out.

<a name="installation"></a>

## 4. Installation

Install with pip:

$ pip install -r requirements.txt

<a name="credits"></a>


Images used in this project were sourced from [Unsplash](https://www.unsplash.com).

## 5. Screenshots

<img src="/static/image/screenshots/01.jpg" width='700'/>
<img src="/static/image/screenshots/02.jpg" width='700'/>
<img src="/static/image/screenshots/03.jpg" width='700'/>
<img src="/static/image/screenshots/04.jpg" width='700'/>
<img src="/static/image/screenshots/06.jpg" width='700'/>
<img src="/static/image/screenshots/07.jpg" width='700'/>
<img src="/static/image/screenshots/08.jpg" width='700'/>
<img src="/static/image/screenshots/09.jpg" width='700'/>

card at the time a session is booked.
- Classes are complimentary with every gym membership.
- Classes and PT sessions may be cancelled at any time before they occur. However, a member only receives a refund of their PT session fee if a cancellation is made 7 days prior to the session or earlier.

## Table of contents

1. [Layout of the app](#layout)
2. [Members Centre](#memberscentre)
3. [Manager's Centre](#managerscentre)
4. [Installation](#installation)

<a name="layout"></a>

## 1. Layout of the app

The gym's home page is accessible via the default route. A horizontal navigation bar and series of tiles featured on this page both allow visitors to navigate to pages where they may view:

- **Classes**: a class timetable displayed in a calendar format
- **PT Sessions**: personal training sessions can be viewed in a calendar format or filtered by trainer
- **Membership**: an explanation of membership and personal training fees.

![image](https://user-images.githubusercontent.com/100200726/226166356-741130c2-28a8-4839-88a7-501d35994b85.png)

All other functions of the app can only be accessed if a user logs in to the members, trainer or manager's centre as described below.

<a name="memberscentre"></a>

## 2. Members Centre

Gym members may login by clicking a link on the home page's horizontal navigation bar:

![home nav bar](https://user-images.githubusercontent.com/100200726/227762142-cb768d18-677f-45a0-bfea-7fa1b767ffc9.jpg)

A member logs in by entering their email address and password. A full list of members' email addresses and passwords is found in the 'member' table created by the SQL file in this repository. However, for ease of reference, the Members Centre can be accessed using:

**Email:** Zhiyi@gmail.com
**Password:** Zhiyi2023

Upon login, a member can access a dropdown menu in the top right hand corner of the screen:

![image](https://user-images.githubusercontent.com/100200726/228117179-b66a7b36-40b1-4521-953b-2c524612e11c.png)

This allows a member to select:

- **My Subscription**: the member can cancel or reactivate their auto-renewing membership subscription. A $100 monthly subscription fee is deducted by way of direct debit on the first of each month unless the member has cancelled it.
- **My Profile**: the member can view and edit their personal profile. They are also able to cancel their membership subscription via their profile.
- **My Bookings**: the member may view existing bookings for classes and PT sessions.
- **My Messages**: the member can review a summary of notifications they have received from the gym regarding payments and bookings. Weekly updates sent by the gym also appear on this page.
- **Reset Password**: the member may reset their password provided the new password has at least eight digits
- **Logout**: the member can log out of the Member Centre and will be redirected to the home page.

Once a member is logged in, they can navigate to 'Classes' or 'PT Sessions' on the horizontal navigation bar and select a class or PT session to book. The system will prevent a member from making a booking if they already have a booking at that time.

<a name="trainercentre"></a>


## 3. Manager's Centre

The gym's manager can login to the Manager's Centre via the _'/admin'_ route using the following details:

**User name:** manager
**Password:** administrator

### Navigation bar option: 'Dashboard'

This link returns the manager to the manager's dashboard. The dashboard features a number of tiles linking to features within the Manager's Centre:

![image](https://user-images.githubusercontent.com/100200726/228355493-c6e9337e-a9d1-407e-b39a-8e41951e3225.png)

### Navigation bar option: 'Members'

If 'Members' is expanded on the vertical navigation bar, the manager will have the option of navigating to:

- **Member List**: this is a list of all gym members. Inactive members are highlighted red. The manager can also filter by member type: active, inactive and archived (futher explanation of these terms is set out below). The manager can click 'view details' to view a member's personal profile. They can then choose whether to edit that profile.
- **Add a member**: the manager can add a new member to the gym's system.

_What is meant by an 'active', 'inactive' and 'archived' member?_

A member is active if they are a current member and their membership subscription payments are up to date.

An inactive member is one was has missed a subscription payment. They can login to the member centre, but cannot book any classes or PT sessions. If they pay subscriptions owing to the gym at the front desk, the manager can reinstate them as an 'active' member.

An 'archived' member is one who has cancelled their subscription and is unlikely to return to the gym. Such members are not deleted from the system, but they cannot log in. This status can be used to design reports where they will not feature. Their data is not archived in the technical sense of being moved and stored in another location.

### Navigation bar option: 'Trainers'

If 'Trainers' is expanded on the vertical navigation bar, the manager will have the option of navigating to:

- **Trainer List**: this is a list of the gym's trainers members. The manager can click 'view details' to view a trainers's personal profile. They can then choose whether to edit that profile. This includes specifying whether a trainer is active or archived (as described below).
- **Add a trainer**: the manager can add a new trainer to the gym's system
- **View Trainer Classes**: the manager can see the total number of classes a trainer has booked within a given date range, and elect to view the details of those classes.

_What is meant by an 'active' or 'archived' trainer?_

A trainer is active if they are a current employee of the gym.

An 'archived' trainer is one who is unlikely to return to the gym. Such trainers are not deleted from the system, but they cannot log in. This status can be used to design reports where they will not feature. Their data is not archived in the technical sense of being moved and stored in another location.

### Navigation bar option: 'Reports'

If 'Reports' is expanded on the vertical navigation bar, the manager will have the option of navigating to:

- **Financial Reports**: this page allows the manager to generate financial reports for a selected period. Revenue is broken down between membership and PT session revenue.
- **Class popularity report**: the manager can create a report showing the popularity of various class types during a selected time period
- **Member Attendance Report**: the manager can generate a report showing the total number of gym attendees during a selected period and the reason for their visit (PT session, class or general gym use).

### Navigation bar option: 'Member weekly update'

The manager can enter details for an update to be sent to members who are subscribing to notifications. This update will appear in a member's 'My messages' section. In addition, the system will automatically send monthly fee reminders to members via the 'myMessage' function outlined in app.py in this repository.

### Navigation bar option: 'Manager'

By clicking on 'manager', the manager has the option of logging out.

<a name="installation"></a>

## 4. Installation

Install with pip:

$ pip install -r requirements.txt

<a name="credits"></a>


Images used in this project were sourced from [Unsplash](https://www.unsplash.com).

## 5. Screenshots

<img src="/static/image/screenshots/01.jpg" width='700'/>
<img src="/static/image/screenshots/02.jpg" width='700'/>
<img src="/static/image/screenshots/03.jpg" width='700'/>
<img src="/static/image/screenshots/04.jpg" width='700'/>
<img src="/static/image/screenshots/06.jpg" width='700'/>
<img src="/static/image/screenshots/07.jpg" width='700'/>
<img src="/static/image/screenshots/08.jpg" width='700'/>
<img src="/static/image/screenshots/09.jpg" width='700'/>
