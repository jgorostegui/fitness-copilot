# Manual Test Checklist - Vision Feature

## Prerequisites
- [ ] Start dev environment: `just dev`
- [ ] Start frontend: `just frontend` (optional, for faster HMR)
- [ ] Open app at http://localhost:5173

---

## 1. Direct Logging (Workout Tab)

### 1.1 Exercise Quick Add
- [ ] Go to **Workout** tab
- [ ] Click **+** button next to an exercise (e.g., "Leg Press")
- [ ] Verify exercise is logged immediately (progress bar updates)
- [ ] Verify **NO chat message** is created
- [ ] Verify "COMPLETED SETS" section shows the logged exercise

### 1.2 Multiple Sets
- [ ] Click **+** multiple times for the same exercise
- [ ] Verify progress bar fills incrementally
- [ ] Verify checkmark appears when all sets are complete

---

## 2. Direct Logging (Nutrition Tab)

### 2.1 Quick Add Buttons
- [ ] Go to **Nutrition** tab
- [ ] Click a quick add button (🍌 Banana, 🥚 Egg, ☕ Coffee, 🥤 Shake)
- [ ] Verify meal is logged immediately
- [ ] Verify **NO chat message** is created
- [ ] Verify calories/protein counters update

### 2.2 Meal Plan Add
- [ ] Click **+** next to a meal in "THE PLAN" section
- [ ] Verify meal is logged and button changes to ✓
- [ ] Verify "CONSUMED" section shows the logged meal

---

## 3. Chat Text Messages

### 3.1 Food Logging via Chat
- [ ] Go to **Chat** tab
- [ ] Type "I ate a chicken salad" and press Enter
- [ ] Verify assistant responds with food analysis
- [ ] Verify ActionCard shows calories logged
- [ ] Go to **Monitor** tab - verify calories updated

### 3.2 Exercise Logging via Chat
- [ ] Type "I did 3 sets of squats at 80kg"
- [ ] Verify assistant responds with exercise logged
- [ ] Verify ActionCard shows sets/reps/weight
- [ ] Go to **Workout** tab - verify exercise appears in completed

---

## 4. Image Upload (LLM_ENABLED=false)

### 4.1 Fallback Message
- [ ] Ensure `LLM_ENABLED=false` in `.env` (default)
- [ ] Go to **Chat** tab
- [ ] Click 📷 camera button
- [ ] Select any image file
- [ ] Verify "Uploading image..." spinner appears briefly
- [ ] Verify fallback message: "I can see you sent an image! For now, please describe what you're showing me..."
- [ ] Verify action_type is "none" (no ActionCard)

---

## 5. Image Upload (LLM_ENABLED=true)

> **Note:** Requires valid `GOOGLE_API_KEY` in `.env`

### 5.1 Gym Equipment Image
- [ ] Set `LLM_ENABLED=true` and add `GOOGLE_API_KEY`
- [ ] Restart backend: `just dev`
- [ ] Go to **Chat** tab
- [ ] Click 📷 and select `demo-images/leg-press.jpg`
- [ ] Verify VisionResponseCard appears with:
  - [ ] Exercise name (e.g., "Leg Press")
  - [ ] Form tips (2-3 bullet points)
  - [ ] Sets/Reps/Weight grid
  - [ ] "✓ Logged" badge
- [ ] Go to **Workout** tab - verify exercise was logged

### 5.2 Food Image
- [ ] Click 📷 and select `demo-images/salad-chicken-breasts.jpg`
- [ ] Verify VisionResponseCard appears with:
  - [ ] Meal name
  - [ ] Macros grid (KCAL, PROTEIN, CARBS, FAT)
  - [ ] "✓ Logged" badge
- [ ] Go to **Monitor** tab - verify calories updated

### 5.3 Unknown Image
- [ ] Click 📷 and select a random image (not food/gym)
- [ ] Verify helpful message: "I'm not sure what this image shows..."
- [ ] Verify no log is created

---

## 6. Monitor Dashboard

### 6.1 Stats Update
- [ ] Go to **Monitor** tab
- [ ] Verify calories consumed matches logged meals
- [ ] Verify protein consumed matches logged meals
- [ ] Verify workouts completed count is correct

### 6.2 Recent Activity
- [ ] Verify recent meals appear in the list
- [ ] Verify recent exercises appear in the list

---

## 7. Profile & Reset

### 7.1 Reset Data
- [ ] Go to **Profile** tab
- [ ] Click "Reset Today's Data"
- [ ] Verify all logs are cleared
- [ ] Verify Monitor shows 0 calories/protein
- [ ] Verify Workout progress bars reset

---

## 8. Error Handling

### 8.1 Network Error
- [ ] Stop the backend
- [ ] Try to send a chat message
- [ ] Verify error is handled gracefully (no crash)

### 8.2 Invalid Image
- [ ] Try to upload a non-image file
- [ ] Verify it's rejected or handled gracefully

---

## Test Results

| Section | Status | Notes |
|---------|--------|-------|
| 1. Direct Logging (Workout) | ⬜ | |
| 2. Direct Logging (Nutrition) | ⬜ | |
| 3. Chat Text Messages | ⬜ | |
| 4. Image Upload (LLM off) | ⬜ | |
| 5. Image Upload (LLM on) | ⬜ | |
| 6. Monitor Dashboard | ⬜ | |
| 7. Profile & Reset | ⬜ | |
| 8. Error Handling | ⬜ | |

**Legend:** ✅ Pass | ❌ Fail | ⬜ Not Tested
