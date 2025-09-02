# Group Planning Feature Documentation

## Overview

This feature allows users who create plans to invite other users by email address to join their outing. The plan will appear in all participants' future outings list.

## How It Works

### 1. Plan Creation Flow (Existing)
- User creates a plan request with group size
- System generates 3 plan suggestions
- User reviews the 3 options

### 2. Plan Confirmation & Group Invitation (NEW)
- User selects one of the 3 plans
- User can optionally add other participants by email
- Maximum participants = original group size - 1 (creator is included)
- System validates emails and looks up users
- Plan is added to all participants' outing history

### 3. Participant Response (NEW)
- Invited users can confirm or decline participation
- Plan status is updated accordingly

## API Endpoints

### 1. Confirm Plan and Add Participants

**POST** `/plans/{plan_id}/confirm`

```json
{
  "plan_id": "string",
  "selected_plan_index": 0,  // 0, 1, or 2
  "participant_emails": ["user1@example.com", "user2@example.com"]
}
```

**Response:**
```json
{
  "message": "Plan confirmed successfully",
  "plan_id": "uuid",
  "confirmed_plan": {
    "plan_id": "uuid",
    "selected_plan_index": 0,
    "creator_user_id": "creator_id",
    "participants": [
      {
        "user_id": "creator_id",
        "email": "creator@example.com",
        "name": "Creator Name",
        "status": "confirmed",
        "invited_at": "2024-01-01T10:00:00Z",
        "confirmed_at": "2024-01-01T10:00:00Z"
      },
      {
        "user_id": "participant_id",
        "email": "participant@example.com",
        "name": "Participant Name",
        "status": "pending",
        "invited_at": "2024-01-01T10:00:00Z"
      }
    ],
    "plan_details": { /* selected plan details */ },
    "group_size": 2,
    "confirmed_at": "2024-01-01T10:00:00Z"
  },
  "participants_added": 1,
  "total_participants": 2
}
```

### 2. Get Confirmed Plan Details

**GET** `/plans/{plan_id}/confirmed`

Returns the confirmed plan with all participant information.

### 3. Respond to Plan Invitation

**POST** `/plans/{plan_id}/participants/{user_id}/respond`

```json
{
  "status": "confirmed"  // or "declined"
}
```

## Frontend Integration

### 1. Plan Selection UI

After the user sees the 3 plan suggestions, add:

```javascript
// Example UI flow
const confirmPlan = async (planId, selectedIndex, participantEmails) => {
  const response = await fetch(`/api/plans/${planId}/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      plan_id: planId,
      selected_plan_index: selectedIndex,
      participant_emails: participantEmails
    })
  });
  
  if (response.ok) {
    const result = await response.json();
    // Show success message
    // Redirect to outing history or plan details
  }
};
```

### 2. Email Input Component

```javascript
const EmailInviteForm = ({ groupSize, onSubmit }) => {
  const [emails, setEmails] = useState([]);
  const maxEmails = groupSize - 1; // minus the creator
  
  return (
    <div>
      <h3>Invite Others (Optional)</h3>
      <p>You can invite up to {maxEmails} additional people</p>
      {emails.map((email, index) => (
        <div key={index}>
          <input
            type="email"
            value={email}
            onChange={(e) => updateEmail(index, e.target.value)}
            placeholder="Enter email address"
          />
          <button onClick={() => removeEmail(index)}>Remove</button>
        </div>
      ))}
      {emails.length < maxEmails && (
        <button onClick={addEmailField}>Add Another Person</button>
      )}
      <button onClick={() => onSubmit(emails)}>Confirm Plan</button>
    </div>
  );
};
```

### 3. Outing History Updates

The outing history will now include group information:

```javascript
// Enhanced outing display
const OutingCard = ({ outing }) => (
  <div className="outing-card">
    <h3>{outing.plan_name}</h3>
    <p>Date: {outing.outing_date}</p>
    <p>Time: {outing.outing_time}</p>
    <p>Group Size: {outing.group_size}</p>
    
    {/* NEW: Group indicator */}
    {outing.is_group_outing && (
      <div className="group-info">
        <p>Group Outing</p>
        <p>Organized by: {outing.creator_user_id === currentUserId ? 'You' : 'Someone else'}</p>
        <div className="participants">
          {outing.participants.map(p => (
            <span key={p.user_id} className={`participant ${p.status}`}>
              {p.name} ({p.status})
            </span>
          ))}
        </div>
      </div>
    )}
    
    {/* NEW: Response buttons for pending invitations */}
    {outing.is_group_outing && 
     getCurrentUserParticipant(outing, currentUserId)?.status === 'pending' && (
      <div className="invitation-response">
        <button onClick={() => respondToInvitation(outing.plan_id, 'confirmed')}>
          Accept
        </button>
        <button onClick={() => respondToInvitation(outing.plan_id, 'declined')}>
          Decline
        </button>
      </div>
    )}
  </div>
);
```

## Data Flow

1. **Plan Creation**: User creates plan → 3 suggestions generated
2. **Plan Confirmation**: User selects plan + emails → System validates emails → Finds users by email → Creates confirmed plan
3. **Outing Addition**: System adds outing to each participant's history
4. **Notifications**: Invited users see pending invitations in their outing history
5. **Responses**: Users can accept/decline → System updates statuses

## Validation Rules

- Email format validation (regex)
- Maximum participants = original group size - 1
- Duplicate email removal
- User existence check (users must be registered)
- Plan must exist and be valid

## Error Handling

- **Invalid emails**: Returns validation error
- **Too many participants**: Returns error with limit
- **User not found**: Skips user with warning
- **Plan not found**: Returns 404
- **Database errors**: Returns 500 with details

## Future Enhancements

1. **Email Notifications**: Send actual emails to invited users
2. **Real-time Updates**: WebSocket for instant invitation updates
3. **Invitation Expiry**: Time limits for responses
4. **Group Chat**: Add messaging for group planning
5. **Role Management**: Different permissions for creator vs participants
