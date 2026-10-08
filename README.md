SQL Injection Lab README - Introduction

SQL Injection Lab

A delibrately vulnerable Flask + SQLite web application created to practice SQL injection discovery, exploitation, database enumeration, remediation, and security testing in a controlled local environment.

Purpose

The purpose of this project is to understand SQL injection from both an attacker's and a developer's perspective.

The lab was built from scratch rather than relying solely on pre-built vulnerable applications. This allowed the SQL queries, application behavior, vulnerability, exploitation process, and remediation to be observed directly.

All testing was performed against a locally hosted application under my control.

Objectives

Understand how SQL queries are constructed by a web application
Identify SQL injection vulnerabilities through application behavior
Understand the SQL context in which user input is inserted
Exploit Boolean-based SQL injection
Perform UNION-based SQL injection
Determine the number of columns in a query
Identify reflected columns
Enumerate the SQLite database schema
Extract information from another database table
Use SQL expressions and string concatenation during data extraction
Filter extracted data using SQL conditions
Remediate SQL injection using parameterized queries
Retest the application after remediation
Extend the lab to blind SQL injection

SQL Injection Lab README - Environment and Application Structure

Lab Environment

The lab was developed and tested locally using:

Python 3.9.6
Flask 3.1.3
SQLite
BurpSuite
macOS

The application was intentionally designed to contain SQL injection vulnerabilities for security testing and was hosted locally during testing.

Application Structure

The application contains two primary endpoints:
/user
The /user endpoint accepts a user ID through the id parameter and retrieves a corresponding record from the users table.
Example: 

/user?id=1
The initial implementation used direct string concatenation to construct the SQL query, making the endpoint vulnerable to SQL injection.

The vulnerable query structure was:

query = "SELECT * FROM users WHERE id = " + user_id

/search
The /search endpoint accepts a search term through the q parameter and searches the products table.

Example:

/search?q=Laptop

The initial implementation constructed the LIKE query using direct concatenation:

query = "SELECT name, description FROM products WHERE name LIKE '%" + search_term + "%'"

This allowed user-controlled input to become part of the SQL statement.

The endpoint was later remediated using a parameterized query:

query = "SELECT name, description FROM products WHERE name LIKE ?"
cursor.execute(query, ("%" + search_term + "%",))

This causes the search term to be treated as data rather than executable SQL syntax.

Database Schema

The SQLite database contains two tables.

users

Column        Type           Description
id            INTEGER        User Identifier
username      TEXT           Username
email         TEXT           Email address
role          TEXT           User role

Example records include regular users and an administrative user.

products

Column        Type           Description
id            INTEGER        Product Identifier
name          TEXT           Product name
description   TEXT           Product description
price         REAL           Product price

The database is generated locally by database.py

The database file itself is intentionally exluded from version control because it can be recreated from the source code.

SQL Injection Lab README - Vulnerability Discovery

SQL Injection Discovery

1. Testing the /user Endpoint

The /user endpoint initially accepted a user-controlled id parameter.

A normal request produced the expected result:

/user?id=1

The application returned the corresponding user record.

I then tested how the application handled unexpected input by adding a single quote:

/user?id=1'

The application returned an internal server error.

This behavior suggested that the input was being inserted into an SQL statement without being safely handled.

2. Confirming SQL injection with Boolean Logic

To determine whether the input could influence the SQL condition, I tested Boolean expressions.

The first test used:

/user?id=1 OR 1=1

The application returned a valid user record.

I then tested:

/user?id=1 AND 1=2

The application returned:

User not found

The two tests produced different results because:

1=1 is always true.
1=2 is always false.
OR can cause the overall condition to evaluate as true.
AND with a false condition causes the overall condition to evaluate as false.

This confirmed that user input was affecting the SQL logic.

3. Understanding the Result

The vulnerable application constructed the query using string concatenation:

query = "SELECT * FROM users WHERE id = " + user_id

For example, supplying:

1 OR 1=1 caused the application to construct a query equivalent to:

SELECT * FROM users WHERE id = 1 OR 1=1

Because 1=1 is always true, the query could return multiple rows.

The application used:

result = cursor.fetchone() so only the first matching row was displayed in the response.

Conclusion

The combination of:

1. An SQL error when supplying a quote.
2. Different application behavior for true and false Boolean conditions
3. Direct concatenation of user-controlled input into the SQL statement

provided sufficient evidence that the /user endpoint was vulnerable to SQL injection.

SQL Injection Lab README - UNION-Based SQL Injection

UNION-Based SQL Injection

1. Testing the /search Endpoint

The /search endpoint searched the products table using the q parameter.

A normal request such as:

/search?q=Laptop returned the matching product.

I first tested a single quote: /search?q='

The application returned a database error: unrecognized token: "'"

This indicated that the input was being inserted into an SQL string context.

2. Confirming Injection in a String Context

The original query was constructed as:

query = "SELECT name, description FROM products WHERE name LIKE '%" + search_term + "%'

The input therefore appeared inside the following SQL structure:

SELECT name, description
FROM products
WHERE name LIKE '%<user_input>%'

I tested Boolean SQL injection using: ' OR '1'='1

The resulting query was approximately:

SELECT name, description
FROM products
WHERE name LIKE '%' OR '1'='1%'

The application returned product records, demonstrating that the input could alter the SQL statement.

3. Determining the Number of Columns

I then tested whether a UNION SELECT could be used to append another result set to the original query.

The original query selected two columns:

SELECT name, description

However, rather than assuming the column count, I tested it experimentally.

A UNION SELECT containing an incorrect number of columns caused the application to return an error indicating that the two sides of the UNION did not have the same number of result columns.

This confirmed that the original query expected two columns.

4. Identifying Reflected Columns

I next supplied two controlled values:

' UNION SELECT 'AAA','BBB' ---

The application reflected both values in its response.

This established that both columns selected by the UNION were visible in the application's response.

The test demonstrated the importance of determining both:

The number of columns required by the UNION
Which columns are reflected to the user

5. Extracting Data from Another Table

Once the column count and reflected columns were established, I used the UNION query to retrieve information from the users table.

For example:

UNION SELECT username, email FROM users

The application returned usernames and email addresses from the second table.

This demonstrated that the SQL injection could be used to access data outside the intended products query.

6. Enumerating the SQLite Schema

Because the application used SQLite, I investigated SQLite's database metadata.

SQLite stores information about database objects in the sqlite_master table.

I queried the table name and table creation statement:

SELECT name, sql
FROM sqlite_master
WHERE type='table'

This revealed the application's database structure, including the products and users tables.

The schema information showed that the users table contained:

id
username
email
role

and that the products table contained:

id 
name 
description
price 

7. Working Within a Two-Column Constraint

The UNION query provided only two output columns, while the users table contained multiple pieces of information that I wanted to observe.

I used SQLite's string concatenation operator (||) to combine multiple values into a single column.

For example:

SELECT username || ':' || email, role
FROM users

This allowed multiple pieces of information to be returned while still satisfying the two-column requirement.

8. Filtering the Extracted Data

Finally, I used a WHERE condition to retrieve only the administrative account:

SELECT username, role
FROM users
WHERE role = 'admin'

The application returned the administrative user.

Conclusion

The UNION-based testing demonstrated the following workflow:

Identify Injection -> Understand SQL context -> Determine column Count -> Identify reflected columns -> Identify database structure -> Retrieve data -> Apply SQL conditions to filter results

The exercise demonstrated how an SQL injection vulnerability can allow an attacker to move from manipulating an application's intended query to accessing information from other database tables.

SQl Injection Lab README - Remediation and Retesting

Remediation

After demonstrating the SQL injection vulnerability, I modified the /search endpoint to prevent user input from being interpreted as SQL syntax.

Vulnerable Implementation

The original implementation constructed the query through string concatenation:

query = "SELECT name, description FROM products WHERE name LIKE '%" + search_term + "%'"
cursor.execute(query)

Because the user-controlled search_term was directly inserted into the SQL statement, an attacker could manipulate the structure of the query.

Parameterized Query

I replaced the vulnerable implementation with a parameterized query:

query = "SELECT name, description FROM products WHERE name LIKE ?"
cursor.execute(query, ("%" + search_term + "%",))

The SQL statement and the user-controlled value are now handled separately.

The % wildcard characters are added to the parameter value rather than being incorporated into the SQL statement itself.

Conceptually, the database receives:

SQL statement:
SELECT name, description FROM products WHERE name LIKE ?

Parameter:
%<user input>%

The input is therefore treated as a value rather than executable SQL syntax.

Retesting

After implementing the parameterized query, I restarted the Flask application and verified that normal product searches continued to work.

For example:
/search?q=Laptop continued to return the expected product.

I then repeated the previously successful UNION-based SQL injection test:
'UNION SELECT username, role FROM users WHERE role = 'admin' --

The application no longer returned the administrative record and instead responded: No products found

The SQL query printed by the application was now:

SELECT name, description FROM products WHERE name LIKE ?

The attacker's input was not incorporated into the SQL statement.

Remediation Result

The retest demonstrated that parameterized queries prevented the previously demonstrated SQL injection technique while preserving the intended search functionality.

Lesson Learned

This lab reinforces several important concepts:

SQL injection occurs when untrusted input can influence the structure of an SQL statement.
Database errors can provide useful clues about the context in which input is being processed.
Boolean conditions can be used to determine whether user input is affecting SQL logic.
UNION-based SQL injection requires the attacker to understand the structure of the original query.
The number of columns in the original query must match the number of columns in the UNION query.
Reflected columns determine which extracted values can be observed through the application response.
Database metadata can reveal information about the underlying schema.
SQL expressions can be used to work within constraints such as a limited number of output columns.
Parameterized queries separate SQL code from user-controlled data.
Security testing should include retesting after remediation to verify that the vulnerability has actually been addressed.

Future Work

The next stage of this project will introduce a blind SQL injection scenario.

Unlike the UNION-based vulnerability demonstrated above, the blind SQL injection lab will not directly expose database query results. Instead, the goal will be to infer information from differences in application behavior.

Planned techniques include:

Boolean-based blind SQL injection
Conditional responses
Inferring database information one condition at a time
Automating repetitive requests where appropriate
Remediation and retesting

SQLi Lab README - Blind SQL Injection

Objective

The next stage of the lab demonstrates blind Boolean-based SQL injection.

Unlike the previous SQL injection tests, the /blind endpoint does not return database records. Instead it returns one of two responses: 
User exists
User not found

This difference can be used as a Boolean oracle to determine whether a SQL condition is true or false.

Vulnerable Endpoint

The /blind endpoint uses user-controlled input directly in a SQL query:

```
query = "SELECT * FROM users WHERE id = " + blind_id

```
The application that returns only whether a matching record exists:

if result:
	return "User exists"

return "User not found"

Because the SQL query is constructed through string concatenation, an attacker can inject additional conditions.

Boolean Testing

A true condition: /blind?id=1 AND 1=1 returns: User exists
A false condition: /blind?id=1 AND 1=2 returns: User not found

This establishes the application's Boolean oracle.

Testing Database Values

The same technique can be used to ask questions about data that the application never directly displays.

For example:
/blind?id=3 AND role = 'admin' returns: User exists while /blind?id=3 AND role = 'user' returns: User not found.

This allows information to be inferred from the application's responses.

Character Extraction

SQLite's SUBSTR() function can be used to examine individual characters.

For example:
/blind?id=3 AND SUBSTR(username, 1, 1) = 'a' returns User exists, revealing that the first character is a. The length can also be determined using: /blind?id=3 AND LENGTH(username) = 5 which returns User exists for the admin account.

Manual Extraction

Characters can be narrowed down using comparison operators instead of testing every character individually.

For example:
/blind?id=3 AND SUBSTR(username, 1, 1) > 'm' can divide the possible characters into two groups.

Repeated comparisons can progressively narrow the search space. This is essentially a blind search, allowing fewer requests than testing every character individually.

Automating Blind SQLi

A Python script was created to automate the extraction process.

The script:
1. Determines the username length.
2. Tests each character position.
3. Uses the application's response as the Boolean oracle.
4. Uses binary search to reduce the number of requests.
5. Reconstructs the username character by character.
6. Accepts the target user ID as a command-line argument.

Example output:

Username length: 5
Position 1: a
Position 2: d
Position 3: m
Position 4: i
Position 5: n
Username: admin

The script was also tested against another user: python blind_sqli.py 1 which successfully extracted: Username: alice

Key Lessons

Blind SQL injection does not require the application to display database contents.
Differences in application behavior can act as a Boolean oracle.
SQL conditions can be used to infer information one bit of information at a time.
LENGTH() can determine the size of unknown values.
SUBSTR() can extract individual characters.
Character comparisons can reduce the number of requests through binary search.
Automation makes blind SQLi practical when extracting larger values.
Parameterized queries prevent user input from being interpreted as SQL syntax.
