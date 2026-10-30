# Tsala Market – UI States

**Project:** Tsala Market  
**Course:** CSI473 – Software Engineering  
**Team:** Team 16  
**Document:** User Interface States  
**Purpose:** CSI473 Laboratory 10 – User-interface, Accessibility and Usability Design

---

## 1. Introduction

This document describes the different user interface states of the Tsala Market system. It identifies how the system should respond to normal user interactions, loading operations, empty results, invalid inputs, errors, unauthorised access and unavailable services.

The purpose is to ensure that users receive clear feedback when interacting with the system, even when an operation cannot be completed successfully.

The document covers three main user perspectives:

1. Smallholder Farmer – checking whether an offered agricultural price is fair.
2. Market Vendor – submitting agricultural market-price information.
3. System Administrator – reviewing and verifying submitted price entries.

The interface states are designed to support the functional requirements, business rules, use cases and quality requirements of Tsala Market.

## 2. Scope

The following system activities are covered:

| Activity | User | Description |
|---|---|---|
| Check My Offer | Farmer | Compare an offered price against verified market prices. |
| View Market Prices | Farmer | View available agricultural commodity prices. |
| Submit Price Entry | Market Vendor | Submit a commodity price for verification. |
| Review Submissions | Administrator | View submitted price entries awaiting review. |
| Verify Price Entry | Administrator | Approve or reject submitted price information. |

## 3. Farmer Interface States

### 3.1 Check My Offer (UC-01)

The Check My Offer functionality allows a farmer to compare an offered agricultural price against the available verified market-price reference.

| State | Trigger/Condition | Expected System Behaviour | User Feedback |
|---|---|---|---|
| Normal | Farmer enters valid commodity, district, unit and offered price. | System normalises the price to P/kg and retrieves the relevant market reference. | Display the comparison result, fairness classification and confidence label. |
| Loading | Farmer submits the offer for checking. | System retrieves the available market-price aggregate. | Display "Checking market prices. Please wait..." |
| Empty | No qualifying verified market-price records exist. | System does not calculate a misleading reference price. | Display "No verified market prices are currently available for this selection." |
| Validation Error | Farmer enters a missing, invalid or non-positive price. | System rejects the invalid input. | Display "Please enter a valid price greater than zero." |
| Unsupported Unit | Farmer selects a unit without a configured conversion factor. | System prevents price normalisation. | Display "This unit is currently not supported. Please select another unit." |
| System Error | The price-check operation fails unexpectedly. | System logs the error and prevents an incorrect result from being displayed. | Display "Unable to check your offer right now. Please try again later." |
| Unavailable | The market-price service or database cannot be reached. | System does not present unavailable data as current market information. | Display "Market-price information is temporarily unavailable." |
| Insufficient Data | Fewer than five qualifying entries or fewer than two different submitters are available. | System does not generate a fairness classification. | Display "Not enough verified market data to assess this offer." |
| Stale Data | The available market-price information is outside the required trailing 30-day window. | System excludes stale records from the reference calculation. | Display "Recent verified market data is unavailable." |

### 3.2 Fair Price Check Result States

The system must display one of the following classifications when sufficient verified data is available.

| Result | Business Rule | Interface Behaviour |
|---|---|---|
| Fair | Offer is no more than 10% below the reference median. | Display "Fair" and the relevant market reference. |
| Below Average | Offer is more than 10%, but no more than 25%, below the reference median. | Display "Below Average" and explain the price difference. |
| Significantly Underpaid | Offer is more than 25% below the reference median. | Display "Significantly Underpaid" and explain the price difference. |

Every successful result must also display:

- The farmer's submitted offer normalised to P/kg.
- The verified market reference median.
- The confidence label.
- A disclaimer explaining that the result is indicative guidance and not a guaranteed selling price.

The interface must not rely on colour alone to communicate the classification. Each result must have a readable text label.

## 4. Market Vendor Interface States

### 4.1 Submit Price Entry

The Submit Price Entry functionality allows market vendors to contribute agricultural price information to the Tsala Market system.

| State | Trigger/Condition | Expected System Behaviour | User Feedback |
|---|---|---|---|
| Normal | Vendor provides all required valid information. | System validates and records the price submission. | Display "Price submitted successfully." |
| Loading | Vendor submits a price entry. | System processes the submission. | Display "Submitting your price entry. Please wait..." |
| Empty | Vendor has not entered any submission information. | System displays the submission form without previous values. | Display the required input fields. |
| Validation Error | Required fields are missing or invalid. | System prevents submission until the errors are corrected. | Display a clear error beside the relevant field. |
| Invalid Price | Vendor enters a zero, negative or invalid price. | System rejects the price. | Display "Enter a valid price greater than zero." |
| Unsupported Unit | Vendor selects a unit without a configured conversion factor. | System prevents normalisation and submission. | Display "Please select a supported price unit." |
| System Error | Submission processing fails. | System records the failure and avoids falsely confirming submission. | Display "Your submission could not be completed. Please try again." |
| Unauthorised | An unauthenticated user attempts to access a protected submission function. | System prevents access to the protected function. | Display "Please log in to continue." |
| Unavailable | The submission service is unavailable. | System does not confirm a submission that was not recorded. | Display "Submission service temporarily unavailable." |
| Offline | The device has no network connection. | System prevents transmission and informs the user. | Display "You are offline. Your submission has not been sent." |

### 4.2 Submission Status

Every submitted price entry must have a clear verification status.

| Status | Meaning | Interface Behaviour |
|---|---|---|
| Pending Verification | Submission has been received but not reviewed. | Display "Awaiting verification." |
| Verified | Submission has passed the verification process. | Display "Verified." |
| Rejected | Submission has been rejected by an administrator. | Display "Rejected" and provide the recorded reason where available. |

Only Verified entries may contribute to Fair Price Check calculations.

## 5. Administrator Interface States

### 5.1 Review and Verify Price Submissions

The administrator interface allows authorised administrators to review submitted agricultural price entries and determine whether they should be verified or rejected.

| State | Trigger/Condition | Expected System Behaviour | User Feedback |
|---|---|---|---|
| Normal | Administrator opens the submission management page. | System retrieves available submissions. | Display the submission list and verification statuses. |
| Loading | Administrator opens or refreshes the submission list. | System retrieves submission records. | Display "Loading price submissions..." |
| Empty | No pending submissions exist. | System displays an empty submission list. | Display "There are currently no submissions awaiting verification." |
| Validation Error | Administrator attempts an invalid action or leaves required information incomplete. | System prevents the action. | Display the relevant validation message. |
| Unauthorised | An unauthorised user attempts to access administrative functions. | System denies access. | Display "You are not authorised to access this page." |
| System Error | The submission retrieval or verification operation fails. | System logs the failure and preserves the existing submission status. | Display "An error occurred. Please try again." |
| Unavailable | Administrative services cannot be reached. | System prevents unconfirmed verification actions. | Display "Verification service is temporarily unavailable." |
| Confirmation | Administrator attempts to verify or reject an entry. | System requests confirmation before changing the status. | Display a confirmation message describing the intended action. |
| Success | Administrator successfully verifies or rejects an entry. | System updates the status and records the administrative action in the audit log. | Display "Submission status updated successfully." |

### 5.2 Verification Rules

- Only authorised administrators may verify or reject price submissions.
- Only submissions that have passed the required checks may be marked Verified.
- Rejected submissions should have a recorded reason.
- Administrative changes must be recorded in immutable audit logs.
- Verification status must be visible to the administrator.
- Unsuccessful operations must not display false success messages.

## 6. Navigation and Recovery Behaviour

The interface should allow users to recover from errors without unnecessarily restarting their tasks.

| Situation | Recovery Behaviour |
|---|---|
| Invalid farmer price | Allow the farmer to correct the entered price. |
| Unsupported unit | Allow the farmer to select another supported unit. |
| Insufficient market data | Allow the farmer to return to commodity or district selection. |
| Network interruption | Inform the user and allow them to retry when connectivity returns. |
| Invalid vendor submission | Preserve valid entered fields where possible and highlight the invalid fields. |
| Failed vendor submission | Allow the vendor to retry after checking the submission status to avoid duplicate entries. |
| Unauthorised administrative access | Direct the user to the login page. |
| Failed verification | Preserve the existing submission status and allow an authorised administrator to retry. |

## 7. Accessibility Considerations

Tsala Market should be accessible and usable by people with different levels of digital literacy and different accessibility needs.

The following accessibility requirements apply to the interface:

1. **Readable Text:** Use clear language, readable font sizes and understandable instructions.
2. **Keyboard Navigation:** All web interface controls must be accessible using a keyboard.
3. **Visible Focus:** Keyboard focus must be clearly visible when navigating between interface elements.
4. **Persistent Labels:** Input fields must have descriptive labels that remain visible.
5. **Clear Validation:** Errors must explain what went wrong and how the user can correct the problem.
6. **Non-Colour Indicators:** Important information must not be communicated through colour alone.
7. **Consistent Navigation:** Navigation controls and page layouts should remain consistent.
8. **Responsive Design:** Web interfaces must adapt to mobile phones, tablets and desktop screens.
9. **Simple Language:** Messages should avoid unnecessary technical terminology.
10. **Screen Reader Support:** Form controls, headings, status messages and error notifications should have appropriate accessible names and semantics.

For the USSD interface, instructions should be short, clearly numbered and easy to follow.

## 8. Design Decisions and Rationale

| Design Decision | Reason | Alternative Considered | Trade-off |
|---|---|---|---|
| Display explicit error messages. | Helps users understand and recover from problems. | Displaying generic error codes. | Requires additional message design and maintenance. |
| Prevent calculations when verified data is insufficient. | Avoids misleading farmers with unreliable price comparisons. | Displaying an estimated price using limited records. | Some users may not receive an immediate result. |
| Use text labels alongside result classifications. | Makes results understandable without depending on colour. | Using colour indicators alone. | Requires additional screen space. |
| Display submission verification statuses. | Helps vendors understand whether their submissions can contribute to market references. | Showing only a submission confirmation. | Requires status management and additional interface elements. |
| Request confirmation before administrative changes. | Reduces accidental verification or rejection. | Applying changes immediately. | Adds an additional interaction step. |

## 9. Traceability to Project Requirements

The following project activities and requirements are supported by the UI states described in this document.

| Project Reference | Requirement/Activity | Related UI States |
|---|---|---|
| UC-01 | Check My Offer | Farmer normal, loading, empty, validation, error and insufficient-data states. |
| Price Submission | Submit agricultural price information | Vendor normal, loading, validation and submission-status states. |
| Price Verification | Review and verify submitted prices | Administrator normal, confirmation, success and unauthorised states. |
| Business Rules | Verified price entries, normalisation and data sufficiency | Insufficient-data, unsupported-unit and stale-data states. |
| Quality Requirements | Usability and accessibility | Accessibility considerations and recovery behaviour. |
| Audit Requirements | Record administrative changes | Administrator verification and rejection states. |

*Note: The named activity references above should be cross-checked against the final approved use-case and requirements identifiers in the project traceability matrix.*

## 10. Conclusion

The UI states defined in this document ensure that Tsala Market provides clear and consistent feedback during normal and exceptional user interactions.

By deliberately designing loading, empty, validation, error, unauthorised, unavailable and stale-data states, the system can provide a more reliable and understandable experience for farmers, vendors and administrators.

These states will guide the development of the Tsala Market wireframes and clickable prototype and will serve as a reference during implementation and usability testing.

