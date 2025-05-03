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

### Users Service:
1. **Create User (POST /users)**
   - *What it does:* Adds a new user to the system.
   - *Why it’s needed:* Enables user onboarding by registering accounts with necessary details like name, email, and preferences.
2. **Retrieve User by ID (GET /users/{id})**
   - *What it does:* Fetches a specific user's information based on their unique ID.
   - *Why it’s needed:* Allows personalized access to a user’s stored details.
3. **Retrieve All Users (GET /users)**
   - *What it does:* Returns a list of all registered users.
   - *Why it’s needed:* Useful for administrative purposes or group-related features, like finding friends or managing event participants.
4. **Update User (PUT /users/{id})**
   - *What it does:* Modifies the details of an existing user.
   - *Why it’s needed:* It allows users to update their information, such as preferences, contact details, passwords, etc.
5. **Delete User (DELETE /users/{id})**
   - *What it does:* Removes a user from the system.
   - *Why it’s needed:* Supports account management, ensuring users can delete their profiles when no longer needed.

### Outing Profile Service:
1. **Create Outing Profile (POST /profiles)**
   - *What it does:* Stores a new outing-profile document for a user—preferred venue types, locations, days, budgets, etc.
   - *Why it’s needed:* Serves as the canonical source of user preferences, which the Planning Service and recommendation logic rely on.recommendations.
2. **Retrieve Outing Profile (GET /profiles/{userId})**
   - *What it does:* Fetches the complete outing profile for a specific user.
   - *Why it’s needed:* Lets UIs and backend services read a user’s historical preferences when generating suggestions or displaying the profile.
3. **Update Outing Profile (PUT /profiles/{userId})**
   - *What it does:* Replaces the existing profile with an updated set of preferences.
   - *Why it’s needed:* Keeps the profile synchronized with the user’s evolving tastes, ensuring future recommendations stay relevant.
4. **Delete Outing Profile (DELETE /profiles/{userId})**
   - *What it does:* Permanently removes the user’s outing-profile and all stored preference data.
   - *Why it’s needed:* upports “reset profile,” account deletion, or GDPR/right-to-be-forgotten requests.

### Venues and Activities Service:
1. **List Venues (GET /venues)**
   - *What it does:* Retrieves a list of all available venues and activities.
   - *Why it’s needed:* Provides users with browsing capabilities to explore all possible activities and venues.
2. **Get Venue Details (GET /venues/{venueId})**
   - *What it does:* Provides detailed information about a specific venue or activity.
   - *Why it’s needed:* Crucial for users who wish to learn more about a venue or activity before making a decision.
3. **Create Venue (POST /venues)**
   - *What it does:* Adds a new venue or activity to the system.
   - *Why it’s needed:* Allows administrators to expand the offerings available to users.
4. **Update Venue (PUT /venues/{venueId})**
   - *What it does:* Modifies details of an existing venue or activity.
   - *Why it’s needed:* Necessary for maintaining accurate and current information on venues and activities.
5. **Delete Venue (DELETE /venues/{venueId})**
   - *What it does:* Removes a venue or activity from the listing.
   - *Why it’s needed:* Helps keep the database clean from outdated or no longer available options.

### Planning Service:
1. **Create Plan (POST /plans)**
   - *What it does:* Allows users to create a new plan for an outing based on selected venues and dates.
   - *Why it’s needed:* Enables the core functionality of organizing outings based on user inputs and preferences.
2. **Retrieve Plan (GET /plans/{planId})**
   - *What it does:* Fetches details of a specific planned outing.
   - *Why it’s needed:* Allows users to review the details and status of their planned outings.
3. **Update Plan (PUT /plans/{planId})**
   - *What it does:* Updates the details of an existing plan.
   - *Why it’s needed:* Provides flexibility to change outing plans as circumstances or preferences change.
4. **Delete Plan (DELETE /plans/{planId})**
   - *What it does:* Deletes an existing outing plan.
   - *Why it’s needed:* Useful for users who wish to cancel or remove planned outings.

### Booking Service:
1. **Redirect to Booking (GET /bookings/{venueId})**
   - *What it does:* Provides a direct link or mechanism to book a selected venue or activity.
   - *Why it’s needed:* Facilitates the booking process by directing users to the appropriate external booking platform.
---

## *User's use cases*

![system components](https://github.com/Lior1305/Planeet/blob/main/users_use_cases.drawio.png)

