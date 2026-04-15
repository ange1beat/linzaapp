# Linza Platform — User Guide

## 1. Sign In

### Email Authentication

1. Open the login page
2. Enter your **email or phone** and **password**
3. Click **"Log in"**
4. The system will send a 6-digit verification code to your email
5. Enter the code and click **"Confirm"**
6. If the code hasn't arrived — click **"Request again"** (available after 25 sec)
7. After confirmation, you will be redirected to the dashboard

### Password Recovery

1. Click **"Forgot your password?"** on the login page
2. Enter your email and follow the instructions

---

## 2. Dashboard

After signing in, you'll see the main page with:
- **Project cards** — your active projects
- **Sidebar** — navigation across sections
- **Favorite projects** — quick access to starred projects

---

## 3. Projects

### Viewing the Project List

- Go to **"Projects"** in the sidebar
- Use **search** to filter by name
- The list supports **pagination** — switch pages at the bottom

### Creating a Project

1. Click **"Create project"**
2. Enter a name (1–50 characters: letters, numbers, spaces, hyphens, underscores)
3. Click **"Create"**

### Project Settings

- Open a project → **"Settings"**
- Change the name or upload a project avatar
- Click **"Apply"**

### Favorites

- Click ★ next to a project to add it to favorites
- Favorite projects appear in the sidebar

### Deleting a Project

- Only the **owner** can delete a project
- Open the project → confirm deletion

---

## 4. Project Members

### Viewing Members

- Open a project → **"Members"** section
- Table: name, email, Telegram, phone, role, actions

### Adding a Member

1. Click **"+ Add members"**
2. Search for a user by name or email
3. Select a role: **Viewer**, **Editor**, or **Owner**
4. Confirm

### Removing a Member

- Click the remove button next to the member
- The project owner cannot be removed

---

## 5. Project Sharing

You can share a project:
- **With a specific user** — they get direct access
- **With a team** — all team members get access
- **With an organization** — all users in the organization get access

Permission levels:
- **view** — read-only access
- **edit** — read and write access

---

## 6. Profile

Go to **"Profile"** (avatar icon in the sidebar):

- **Name** — change first and last name
- **Password** — change password (min. 8 chars, uppercase, lowercase, digits, special characters)
- **Telegram** — link your Telegram account
- **Avatar** — upload a profile picture

---

## 7. Teams (Administrator role)

Available when the **administrator** portal role is active.

### Viewing

- Go to **"Teams"** in the sidebar
- List of teams with member counts

### Creating a Team

1. Click **"Create team"**
2. Enter a name
3. Confirm

### Managing Members

- Open a team → member table
- Add or remove members

---

## 8. Storage (Administrator role)

Available when the **administrator** portal role is active.

- **My usage** — personal quota, team quota, organization quota
- **All quotas** — table with type, size, and usage percentage
- Quotas are hierarchical: user < team < organization

---

## 9. Role Switching

If you have multiple portal roles assigned, you can switch between them:

| Role | Access |
|------|--------|
| **Administrator** | Organization settings, users, teams, storage |
| **Operator** | File management, analysis, queue |
| **Lawyer** | Review of escalated content |
| **Chief Editor** | Team metrics, content marking |

To switch: select the desired role from the dropdown in the sidebar.

---

## 10. Sign Out

Click **"Sign out"** in the sidebar. Your session will be terminated and the JWT token invalidated.
