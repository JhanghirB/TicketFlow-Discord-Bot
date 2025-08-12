# TicketFlow Discord Bot

TicketFlow is a Python-based Discord bot built with the Nextcord library to manage purchase request tickets in a Discord server. The bot automates private ticket creation, guides users through a message-driven purchase flow, and manages role-based access for closed tickets, ensuring an organized and secure ticketing process.

---

## Features

- **Private Ticket Channels**
  - Creates dedicated text channels for each user’s purchase request.
  - Restricts visibility to the requesting user, bot, and staff roles.
  
- **Interactive Ticket Workflow**
  - Guides users through staged prompts to confirm purchase details.
  - Supports alias recognition for specific products (e.g., vehicle names) with flexible keyword matching.
  - Includes message-based branching for “Yes/No” decisions.

- **Role-Based Ticket Closure**
  - Staff members can close tickets via an in-channel button.
  - Closed tickets become visible only to designated ticket manager roles.

- **Persistent State Tracking**
  - Uses a JSON file to store ticket states (stage, confirmation status).
  - Maintains progress across bot restarts without losing ticket data.

- **Setup and Management**
  - Slash command to post a ticket creation embed with a clickable “Create Ticket” button.
  - Optional “Refresh” keyword to reset the ticket stage.

---

## How It Works

1. **Ticket Creation**
   - A user clicks the “Create Ticket” button.
   - A private channel is created and initialized to stage 0.

2. **Stage Progression**
   - Stage 0: Bot prompts for requested items.
   - Stage 5: Bot confirms selections (Yes/No).
   - Stage 20: Bot finalizes with terms and conditions confirmation.

3. **Closure**
   - Users or staff click the “Close Ticket” button.
   - Ticket becomes hidden from the user and visible only to the manager role.

---

## Use Case

TicketFlow is ideal for Discord servers that handle regular purchase or service requests, providing an automated, structured, and secure workflow that scales to large communities while keeping requests organized.

