============
nhs-listpull
============

To provide Email Vision with a daily feed of current segmented customer data for 
targeted email campaigns, and fed through the Email Vision API to Campaign 
Commander which then applies each segment to the proper trigger email.

Initial Phase of Project
------------------------

The application needs to look at customer order data and discern the
following:

Time To Re-Order Email Pulls
----------------------------

-   Does the customer qualify for being sent an email?

-   Does the customer have an email? [If no, disqualify]
-   Is the customer’s email in the Do Not Email list? [If yes, then
    disqualify]
-   Did the customer’s email come from Amazon.com [If yes, then
    disqualify]

-   Is the product that the customer ordered an autoship?  [If yes,
    exclude the autoship product ordered from the logic of this program
    and put this autoship in the autoship basket.  Keep the non-autoship
    product in the order remaining in this program]
-   Has the qualified email customer made a purchase within the last 90
    days?  

If yes, apply the following logic:

-   How many bottles did the customer order of the same product?
-   When did the order with all of the bottles ship?
-   From the order’s shipment date add 5 days and then IDENTIFY which
    orders are at the end of use to QUALIFY for the email.  Please see
    examples below:

Examples 
--------

** Example 1

John Doe ordered one bottle of Flora Source July 1<sup>st</sup>, 2013. 
John’s order shipped out July 2^nd^.  35 days from July 2^nd^ is August
6<sup>th</sup>, 2013.  This customer’s email address, name, and product 
purchased would then be sent to the Email Vision API for an August 
6<sup>th</sup> email send.

** Example 2

(With Assumption program is built and running on August
6<sup>th</sup>):  Jane Brown ordered 3 bottles of Arthrozyme May 1<sup>st</sup>, 
2013. Jane’s ordered shipped the next day, May 2^nd^, 2013.  95 days from May
1<sup>st</sup> is August 6<sup>th</sup>, 2013.  This customer’s email address, 
name, and product purchased would then be sent to the Email
Vision API for a August 6<sup>th</sup> email send.

** Example 3

Jeff Picaname orders 1 bottle of Arthrozyme Plus and two bottles of Flora Source 
on June 1<sup>st</sup>, 2013.  Jeff’s order shipped out June 2^nd^, 2013.  Jeff 
would have his first product QUALIFY for an email send on July 6<sup>th</sup> 
for the single-bottle purchase of Flora Source which is 35 days from when it 
shipper on June 2^nd^.  Then the second product Jeff ordered (Arthrozyme Plus) 
would QUALIFY for an email send on August 6<sup>th</sup>, 65 days from the 
shipment date.

Autoship Email Pulls
--------------------

* What is the product on autoship?
* When is that product due to ship next?
* Is the product scheduled to ship in the next seven days?

**Rule:**  This part of the program is only concerned with the next
autoship scheduled to ship 7 days out.

**Strategy**:  If we can identify these autoships then we can target
them for upsell and cross sell opportunities before their package ships
and then they are guaranteed free shipping along with getting both
products at the same time.

**Re-Engagement Email Pulls:**

-   Has the customer not ordered anything 120-days or more and has an
    Email?  [If yes, they qualify for re-engagement]
-   What product did this customer order last?  [This customer gets
    segmented into Re-Engagement Email bucket and sub-segmented by last
    product purchased]

**Category Cross-Sell Email Pulls:**

-   Has the customer ordered in last 48 hours?  [If yes they qualify]
-   What is the product they ordered?
-   Based on the product they ordered what category does it apply to
    (e.g., Digestive Health, Heart Health, Joint & Muscle Health, Energy
    Health)?
-   Include customers who have ordered autoship as we are identifying
    what category they belong to for cross-sell

Emails are sent to SmartFocus by Category Buckets.

**Entire House File No-Autoship Email Pull:**

-   Excludes autoship customers with email
-   Excludes people on the most recent Do Not Email file

**Entire House File Including Autoships:**

-   Includes autoship customers
-   Excludes Do Not Email customers

Program Logic
-------------

So basically this program needs to keep track of what it has sent over to Email 
Vision so we don't do duplication.

If in Example 1, John Doe’s email is sent to Email Vision via the API, on August
6<sup>th</sup>.  On August 7<sup>th</sup> John Doe would not have his name resent to the
Email Vision platform.  Nor would it August 8<sup>th</sup>, 9<sup>th</sup>, 10<sup>th</sup>, etc… 

John Doe would only get re-inserted back into the program if he makes a new 
purchase (and same timing criteria would apply).

Should John Doe not purchase after the program does the initial hand-off to
Email Vision, within Email Vision itself we can build out additional email 
campaigns to non-responders based on timing and purchasing rules.  So the 
initial goal here is to do the baton pass-off of qualifying a customer by 
knowing:

* Are they autoship?  [If yes some or all of their order goes into a Autoship 
bucket]
* Are they 35 days out from ship date and have an email?  [If yes then they 
come over]
* Are they previous customers who have made a purchase but not within the last 
90 days?  [They come-over as re-engagers]

Additional Notes
----------------

It would be nice to have a User Interface panel and hit the send button to 
Email Vision. This would keep the clutter of inactive lists from being sent 
over into the platform.  For example, we won’t need to send to the entire house 
file every day, and so on and so forth.

Can the application:

* Pull the lists according to the spec?
* After the initial week your application generates the first list (let's say 
it is the FloraSource Time-To-ReOrder capturing the buyers who purchased FS 30 
or 60 days ago), your app generates the list, we email those people, then it is 
week two, we need a new list.  Will the app know to suppress those initial FS 
buyers and give me new buyers who have not been pulled in the previous list? 
It's like a water fall going into tiered buckets.
 
Bucket 1 spills into Bucket 2, Bucket 2 spills into Bucket 3 and so on....The 
"spill" is the same initial pulled list moving into the different email 
campaigns, each new iteration of responders being suppressed.
 
Each week new customers flow into Bucket 1.  The App needs to know how to 
differentiate that.