# Tsala Market – Accessibility Checklist

## 1. Purpose

This checklist is used to review the accessibility and usability of the Tsala Market interface developed for CSI473 Lab 10.

Tsala Market is intended to help smallholder farmers in Botswana access agricultural market-price information and make more informed selling decisions. The interface should therefore be understandable and usable by people with different levels of digital experience, including users accessing the system through different devices or interaction methods.

The checklist focuses on the following user journeys:

- **Farmer:** Check My Offer (UC-01).
- **Market Vendor:** Submit a Market Price.
- **Administrator:** Review and verify submitted prices.

This document records the accessibility requirements to check, the evidence observed, and any corrective action required. An item must not be marked as passed until it has been checked against the prototype or implemented interface.

## 2. How to use this checklist

For each item, select one status:

- **Pass:** The requirement has been checked and satisfied.
- **Fail:** The requirement has been checked and a problem was found.
- **Not tested:** The requirement has not yet been checked.
- **Not applicable:** The requirement does not apply to the interface being reviewed.

Record evidence or observations for each checked item. Where an item fails, add the issue to the corrective-action table in Section 8.

## 3. Keyboard accessibility

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A01 | All interactive controls can be reached using the keyboard. | Not tested | |
| A02 | Users can move through controls in a logical order using the Tab key. | Not tested | |
| A03 | The keyboard focus indicator is clearly visible. | Not tested | |
| A04 | Users can activate buttons and controls using the keyboard. | Not tested | |
| A05 | Keyboard users can open and close menus, dialogs, and other interactive elements where present. | Not tested | |
| A06 | Keyboard focus is not trapped in an interface element without a clear way to leave it. | Not tested | |
| A07 | The interface does not require a mouse-only action to complete a task. | Not tested | |

## 4. Text, labels, and instructions

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A08 | Every form field has a clear, persistent label. | Not tested | |
| A09 | Instructions explain what information the user must enter. | Not tested | |
| A10 | Required fields are clearly identified. | Not tested | |
| A11 | Labels and instructions use simple, understandable language. | Not tested | |
| A12 | Abbreviations and technical terms are explained where necessary. | Not tested | |
| A13 | Units are clearly displayed for price and quantity fields (for example, P/kg or P per 20 kg). | Not tested | |
| A14 | Confirmation messages clearly explain what has happened and what the user should do next. | Not tested | |
| A15 | Important information is not communicated through placeholder text alone. | Not tested | |

## 5. Colour, contrast, and visual presentation

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A16 | Text has sufficient contrast against its background. | Not tested | |
| A17 | Buttons and important interface controls are visually distinguishable. | Not tested | |
| A18 | Colour is not the only way to communicate a status or result. | Not tested | |
| A19 | Price classifications include descriptive text or another non-colour indicator. | Not tested | |
| A20 | Error messages are distinguishable from normal instructions and information. | Not tested | |
| A21 | Text remains readable without requiring users to interpret small or crowded content. | Not tested | |
| A22 | Content remains usable when the display is resized or zoomed. | Not tested | |

## 6. Forms, validation, and error recovery

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A23 | Users are informed when a required field has been left empty. | Not tested | |
| A24 | Invalid input is identified clearly. | Not tested | |
| A25 | Error messages explain how the user can correct the problem. | Not tested | |
| A26 | Errors are associated with the relevant fields. | Not tested | |
| A27 | Valid information is retained when a form submission fails, where technically possible. | Not tested | |
| A28 | Users receive confirmation after a successful submission. | Not tested | |
| A29 | Users can review important information before completing a consequential action. | Not tested | |
| A30 | Unsupported units or invalid price values are explained in understandable language. | Not tested | |

## 7. Task-specific accessibility checks

### 7.1 Farmer – Check My Offer (UC-01)

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A31 | The farmer can identify how to start the Check My Offer task. | Not tested | |
| A32 | Commodity and district selection instructions are clear. | Not tested | |
| A33 | The offered price and quantity or unit are clearly requested. | Not tested | |
| A34 | The system makes the price unit and any conversion understandable. | Not tested | |
| A35 | The result explains the reference price and classification in plain language. | Not tested | |
| A36 | The result communicates when there is insufficient verified market data. | Not tested | |
| A37 | The result communicates the age or freshness of the market-price information. | Not tested | |
| A38 | Any confidence information or limitations are explained clearly. | Not tested | |
| A39 | The interface makes clear that the result is guidance and not a guaranteed selling price. | Not tested | |

### 7.2 Market Vendor – Submit a Market Price

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A40 | The vendor can identify how to submit a market-price entry. | Not tested | |
| A41 | Commodity, market or district, price, and unit fields are clearly labelled. | Not tested | |
| A42 | The vendor can understand which fields are required. | Not tested | |
| A43 | The vendor receives understandable feedback when an entry is invalid. | Not tested | |
| A44 | The interface explains whether the submission was received and whether it is awaiting verification. | Not tested | |
| A45 | The vendor is not led to believe that an unverified submission is already a verified market price. | Not tested | |

### 7.3 Administrator – Review and Verify Prices

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A46 | Review and verification actions are clearly labelled. | Not tested | |
| A47 | The administrator can distinguish pending, verified, and rejected entries without relying on colour alone. | Not tested | |
| A48 | Relevant submission details are presented clearly before a decision is made. | Not tested | |
| A49 | The result of a verification or rejection action is clearly communicated. | Not tested | |
| A50 | Unauthorised users are not shown controls that allow them to perform administrator actions. | Not tested | |

## 8. Responsive layout and different access conditions

| ID | Accessibility check | Status | Evidence / observation |
|---|---|---|---|
| A51 | The interface remains usable on a small mobile screen. | Not tested | |
| A52 | Important content and controls do not overlap or become hidden at smaller screen sizes. | Not tested | |
| A53 | Users can identify the current page or step in a multi-step task. | Not tested | |
| A54 | Loading states provide feedback that the system is processing a request. | Not tested | |
| A55 | Empty, unavailable, and error states explain what happened and what the user can do next. | Not tested | |
| A56 | Where offline or connection-loss behaviour is represented, users receive clear feedback and recovery instructions. | Not tested | |
| A57 | Stale market-price information is clearly identified where it is displayed. | Not tested | |

## 9. Corrective-action record

Record every failed check and the change made to address it. Do not record a change as completed until the revised prototype or interface has been checked.

| Checklist ID | Problem observed | Corrective action | Verification method | Status |
|---|---|---|---|---|
| | | | | Pending |
| | | | | Pending |
| | | | | Pending |

## 10. Accessibility review summary

Complete this section after testing the prototype or interface.

| Review information | Result |
|---|---|
| Date of review | To be completed |
| Reviewer(s) | To be completed |
| Interface or prototype version | To be completed |
| Number of checks passed | To be completed |
| Number of checks failed | To be completed |
| Number of checks not tested | To be completed |
| Number of checks not applicable | To be completed |

### Most important accessibility issue

To be completed after the review.

### Change made to improve accessibility

To be completed after the review.

### How the change was verified

To be completed after the revised interface was checked.

## 11. Evidence to retain

The following evidence should be retained with the Lab 10 submission where applicable:

- Screenshots of the farmer, vendor, and administrator interfaces.
- Evidence of visible keyboard focus and keyboard navigation.
- Examples of clear field labels and validation messages.
- Examples of status messages that do not rely on colour alone.
- Screenshots showing responsive layouts at different screen sizes.
- A record of accessibility issues discovered and the changes made.
- Evidence that the revised interface was checked after changes.

Screenshots should support the review, but they should not replace the editable wireframe or prototype source files.

## 12. Conclusion

The accessibility review helps ensure that Tsala Market can be understood and used by its intended users, particularly smallholder farmers and market vendors who may have different levels of digital experience.

The checklist covers keyboard access, visible focus, labels, instructions, colour-independent status indicators, form validation, error recovery, responsive layouts, and the clarity of important market-price information.

The review is considered complete only after the applicable checks have been performed, issues have been recorded, and important accessibility problems have been addressed and rechecked.