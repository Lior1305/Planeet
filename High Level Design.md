# **High Level Design**  
*Lior Berlin | Dar Toledano | Nika Klimenchuk*

---

## *Overview*
Planeet revolutionizes the way you plan group meetups by effortlessly merging user preferences with real-time venue availability. Whether it's a spontaneous dinner, a movie night, or an adventurous meetup, Planeet simplifies the planning process, making it easy, fast, and tailored just for you. Input your group's preferences and schedule, and let Planeet handle the rest, from providing personalized recommendations to seamless booking redirections to external sites. Dive into a world of stress-free planning and enrich your social experiences with Planeet—where every meetup is a breeze.

---

## *Problem Statement*
**Planning group outings presents two major challenges:**
- **Mental Effort:** Brainstorming and organizing activities that align with everyone’s preferences is time-consuming.
- **Coordination Complexity:** Synchronizing availability with venues and balancing diverse schedules is difficult.

**These challenges often result in:**
- Delayed decision-making.
- Indecision that prevents plans from materializing.
- Abandoned outings due to frustration.

---

## *Solution Overview*
A web-based application that streamlines group outing planning by:
- Allowing users to input preferences, schedules, and location.
- Integrating real-time venue data (availability, capacity, activity type).
- Providing tailored recommendations to facilitate quick and collaborative decision-making.

---

## *Alternatives & Existing Approaches*
Users currently rely on various methods to plan outings, each with significant limitations:
- **Manual Online Search & Social Media:** Browsing platforms like Google, TripAdvisor, Instagram, or TikTok requires manual comparisons and lacks real-time availability.
- **Asking Friends & Family:** Relies on personal recommendations but offers limited personalization and scheduling flexibility.
- **Local Event Apps & Pre-Defined Itineraries:** Platforms like Meetup, Eventbrite, or influencer itineraries provide inspiration but lack adaptability for custom plans.
- **Spontaneous Exploration & Concierge Services:** Walking around in search of activities is inefficient, while concierge services are costly and cater more to travelers.
- **Using Multiple Specialized Apps:** Booking separately through Ontopo, TripAdvisor, or ClassPass requires juggling multiple platforms without central coordination.

---

## *Components / Services*

![system components](https://github.com/Lior1305/Planeet/blob/main/system_components.drawio.png)

---

## *Rest APIs*

#### users service:
1. **Create User (POST /users)**
*What it does:* Adds a new user to the system.
*Why it’s needed:* Enables user onboarding by registering accounts with necessary details like name, email, and preferences.
2. **Retrieve User by ID (GET /users/{id})**
*What it does:* Fetches a specific user's information based on their unique ID.
*Why it’s needed:* Allows personalized access to a user’s stored details.
3. **Retrieve All Users (GET /users)**
*What it does:* Returns a list of all registered users.
*Why it’s needed:* Useful for administrative purposes or group-related features, like finding friends or managing event participants.
4. **Update User (PUT /users/{id})**
*What it does:* Modifies the details of an existing user.
*Why it’s needed:* It allows users to update their information, such as preferences, contact details, passwords, etc.
5. **Delete User (DELETE /users/{id})**
*What it does:* Removes a user from the system.
*Why it’s needed:* Supports account management, ensuring users can delete their profiles when no longer needed.

####  Preferences service:

####  Vanues and Activities service:

####  Planning service:

####  Booking service:

---

## *User's use cases*

![system components](https://github.com/Lior1305/Planeet/blob/main/users_use_cases.drawio.png)

