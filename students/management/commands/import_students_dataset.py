"""Management command to import the 240 student dataset provided by the user."""
import sys
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from academics.models import Department, Course
from students.models import Student

RAW_STUDENTS_DATA = """
STU-CSE1-001	Manav Mishra	SAMPLE-2026-CSE-001	Computer Science and Engineering (CSE)	First Year	OBC	Male	2006-11-24	0000000000 (dummy)	student001.cse1@example.com	2026	Amravati	90.2	6.6	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-002	Ayush Deshmukh	SAMPLE-2026-CSE-002	Computer Science and Engineering (CSE)	First Year	OBC	Male	2006-03-13	0000000000 (dummy)	student002.cse1@example.com	2026	Aurangabad	90.1	7.95	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-003	Amruta Wankhede	SAMPLE-2026-CSE-003	Computer Science and Engineering (CSE)	First Year	NT-C	Female	2006-10-30	0000000000 (dummy)	student003.cse1@example.com	2026	Amravati	63.1	6.48	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-004	Vivaan Suryawanshi	SAMPLE-2026-CSE-004	Computer Science and Engineering (CSE)	First Year	EWS	Male	2006-09-16	0000000000 (dummy)	student004.cse1@example.com	2026	Amravati	83.3	8.72	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-005	Krishna Patil	SAMPLE-2026-CSE-005	Computer Science and Engineering (CSE)	First Year	SBC	Male	2006-12-26	0000000000 (dummy)	student005.cse1@example.com	2026	Nashik	70.4	8.15	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-006	Tanmay Bansod	SAMPLE-2026-CSE-006	Computer Science and Engineering (CSE)	First Year	SC	Male	2006-01-04	0000000000 (dummy)	student006.cse1@example.com	2026	Jalgaon	78.1	6.75	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-007	Saanvi Gaikwad	SAMPLE-2026-CSE-007	Computer Science and Engineering (CSE)	First Year	NT-B	Female	2006-04-21	0000000000 (dummy)	student007.cse1@example.com	2026	Nagpur	65.5	5.94	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-008	Pooja Desai	SAMPLE-2026-CSE-008	Computer Science and Engineering (CSE)	First Year	EWS	Female	2006-06-26	0000000000 (dummy)	student008.cse1@example.com	2026	Yavatmal	92.7	8.78	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-009	Vaishnavi Thakre	SAMPLE-2026-CSE-009	Computer Science and Engineering (CSE)	First Year	OBC	Female	2006-10-02	0000000000 (dummy)	student009.cse1@example.com	2026	Nashik	65	6.82	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-010	Rahul Kamble	SAMPLE-2026-CSE-010	Computer Science and Engineering (CSE)	First Year	EWS	Male	2006-11-18	0000000000 (dummy)	student010.cse1@example.com	2026	Pune	83.9	8.67	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-011	Simran Dange	SAMPLE-2026-CSE-011	Computer Science and Engineering (CSE)	First Year	ST	Female	2006-01-24	0000000000 (dummy)	student011.cse1@example.com	2026	Yavatmal	99.4	9.35	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-012	Janvi Gawande	SAMPLE-2026-CSE-012	Computer Science and Engineering (CSE)	First Year	NT-C	Female	2006-02-21	0000000000 (dummy)	student012.cse1@example.com	2026	Yavatmal	79.2	9.25	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-013	Sai Dawande	SAMPLE-2026-CSE-013	Computer Science and Engineering (CSE)	First Year	NT-B	Male	2006-03-25	0000000000 (dummy)	student013.cse1@example.com	2026	Pune	70	6.7	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-014	Om Shaikh	SAMPLE-2026-CSE-014	Computer Science and Engineering (CSE)	First Year	OBC	Male	2006-12-16	0000000000 (dummy)	student014.cse1@example.com	2026	Washim	86.1	7.9	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-015	Nikhil Pund	SAMPLE-2026-CSE-015	Computer Science and Engineering (CSE)	First Year	SC	Male	2006-05-06	0000000000 (dummy)	student015.cse1@example.com	2026	Chandrapur	76.4	9.95	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-016	Myra Nimje	SAMPLE-2026-CSE-016	Computer Science and Engineering (CSE)	First Year	SBC	Female	2006-11-24	0000000000 (dummy)	student016.cse1@example.com	2026	Wardha	88	9.29	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-017	Priya Khan	SAMPLE-2026-CSE-017	Computer Science and Engineering (CSE)	First Year	ST	Female	2006-01-29	0000000000 (dummy)	student017.cse1@example.com	2026	Amravati	92.6	7.31	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-018	Nandini Chavan	SAMPLE-2026-CSE-018	Computer Science and Engineering (CSE)	First Year	ST	Female	2006-02-03	0000000000 (dummy)	student018.cse1@example.com	2026	Washim	95.3	6.92	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-019	Parth Bhoyar	SAMPLE-2026-CSE-019	Computer Science and Engineering (CSE)	First Year	NT-D	Male	2006-12-02	0000000000 (dummy)	student019.cse1@example.com	2026	Nashik	95.6	8.39	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-020	Shreya Rathod	SAMPLE-2026-CSE-020	Computer Science and Engineering (CSE)	First Year	VJ/DT	Female	2006-03-15	0000000000 (dummy)	student020.cse1@example.com	2026	Akola	71.4	8.03	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-021	Aarav Kadam	SAMPLE-2026-CSE-021	Computer Science and Engineering (CSE)	First Year	EWS	Male	2006-05-15	0000000000 (dummy)	student021.cse1@example.com	2026	Nashik	96.1	7.3	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-022	Atharv Dhole	SAMPLE-2026-CSE-022	Computer Science and Engineering (CSE)	First Year	SC	Male	2006-04-23	0000000000 (dummy)	student022.cse1@example.com	2026	Buldhana	80.8	8.9	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-023	Pranav Tiwari	SAMPLE-2026-CSE-023	Computer Science and Engineering (CSE)	First Year	SC	Male	2006-02-26	0000000000 (dummy)	student023.cse1@example.com	2026	Aurangabad	68.1	8.56	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-024	Aditi More	SAMPLE-2026-CSE-024	Computer Science and Engineering (CSE)	First Year	OBC	Female	2006-11-02	0000000000 (dummy)	student024.cse1@example.com	2026	Nashik	76.5	9.98	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-025	Riya Mahajan	SAMPLE-2026-CSE-025	Computer Science and Engineering (CSE)	First Year	VJ/DT	Female	2006-09-28	0000000000 (dummy)	student025.cse1@example.com	2026	Buldhana	94.7	5.55	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-026	Mansi Singh	SAMPLE-2026-CSE-026	Computer Science and Engineering (CSE)	First Year	SBC	Female	2006-02-28	0000000000 (dummy)	student026.cse1@example.com	2026	Yavatmal	91.2	7.03	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-027	Abhishek Jadhav	SAMPLE-2026-CSE-027	Computer Science and Engineering (CSE)	First Year	NT-C	Male	2006-05-31	0000000000 (dummy)	student027.cse1@example.com	2026	Akola	79.2	9.79	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-028	Tejas Borkar	SAMPLE-2026-CSE-028	Computer Science and Engineering (CSE)	First Year	SBC	Male	2006-05-15	0000000000 (dummy)	student028.cse1@example.com	2026	Akola	81.3	5.98	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-029	Rutuja Yadav	SAMPLE-2026-CSE-029	Computer Science and Engineering (CSE)	First Year	VJ/DT	Female	2006-11-17	0000000000 (dummy)	student029.cse1@example.com	2026	Aurangabad	81.3	6.4	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-030	Arjun Kulkarni	SAMPLE-2026-CSE-030	Computer Science and Engineering (CSE)	First Year	SC	Male	2006-07-11	0000000000 (dummy)	student030.cse1@example.com	2026	Buldhana	98.2	9.65	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-031	Siddharth Kale	SAMPLE-2026-CSE-031	Computer Science and Engineering (CSE)	First Year	EWS	Male	2006-01-01	0000000000 (dummy)	student031.cse1@example.com	2026	Pune	80.6	6	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-032	Kunal Sharma	SAMPLE-2026-CSE-032	Computer Science and Engineering (CSE)	First Year	VJ/DT	Male	2006-07-05	0000000000 (dummy)	student032.cse1@example.com	2026	Wardha	64.2	9.45	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-033	Diya Joshi	SAMPLE-2026-CSE-033	Computer Science and Engineering (CSE)	First Year	OBC	Female	2006-02-10	0000000000 (dummy)	student033.cse1@example.com	2026	Jalgaon	80.5	5.81	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-034	Neha Ingole	SAMPLE-2026-CSE-034	Computer Science and Engineering (CSE)	First Year	SC	Female	2006-09-30	0000000000 (dummy)	student034.cse1@example.com	2026	Akola	87.1	9.76	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-035	Trisha Gupta	SAMPLE-2026-CSE-035	Computer Science and Engineering (CSE)	First Year	VJ/DT	Female	2006-03-26	0000000000 (dummy)	student035.cse1@example.com	2026	Buldhana	95.2	7.4	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-036	Chaitanya Shinde	SAMPLE-2026-CSE-036	Computer Science and Engineering (CSE)	First Year	SBC	Male	2006-04-19	0000000000 (dummy)	student036.cse1@example.com	2026	Jalgaon	88.2	8.71	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-037	Prachi Mankar	SAMPLE-2026-CSE-037	Computer Science and Engineering (CSE)	First Year	NT-B	Female	2006-07-24	0000000000 (dummy)	student037.cse1@example.com	2026	Chandrapur	96.2	7.53	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-038	Anushka Verma	SAMPLE-2026-CSE-038	Computer Science and Engineering (CSE)	First Year	ST	Female	2006-05-07	0000000000 (dummy)	student038.cse1@example.com	2026	Nagpur	74.8	8.15	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-039	Reyansh Pawar	SAMPLE-2026-CSE-039	Computer Science and Engineering (CSE)	First Year	EWS	Male	2006-04-28	0000000000 (dummy)	student039.cse1@example.com	2026	Wardha	62.3	8.69	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-040	Yash Raut	SAMPLE-2026-CSE-040	Computer Science and Engineering (CSE)	First Year	ST	Male	2006-01-31	0000000000 (dummy)	student040.cse1@example.com	2026	Nagpur	96.4	9.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-041	Ananya Mishra	SAMPLE-2026-CSE-041	Computer Science and Engineering (CSE)	First Year	SBC	Female	2006-02-06	0000000000 (dummy)	student041.cse1@example.com	2026	Wardha	72.6	7.68	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-042	Kavya Deshmukh	SAMPLE-2026-CSE-042	Computer Science and Engineering (CSE)	First Year	SC	Female	2006-10-04	0000000000 (dummy)	student042.cse1@example.com	2026	Jalgaon	97.5	8.07	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-043	Shruti Wankhede	SAMPLE-2026-CSE-043	Computer Science and Engineering (CSE)	First Year	ST	Female	2006-08-31	0000000000 (dummy)	student043.cse1@example.com	2026	Chandrapur	92.7	6.36	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-044	Harsh Suryawanshi	SAMPLE-2026-CSE-044	Computer Science and Engineering (CSE)	First Year	NT-C	Male	2006-02-19	0000000000 (dummy)	student044.cse1@example.com	2026	Pune	78.1	7.6	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-045	Dev Patil	SAMPLE-2026-CSE-045	Computer Science and Engineering (CSE)	First Year	OBC	Male	2006-01-28	0000000000 (dummy)	student045.cse1@example.com	2026	Amravati	77.3	7.03	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-046	Komal Bansod	SAMPLE-2026-CSE-046	Computer Science and Engineering (CSE)	First Year	ST	Female	2006-02-25	0000000000 (dummy)	student046.cse1@example.com	2026	Wardha	69.2	7.52	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-047	Aditya Gaikwad	SAMPLE-2026-CSE-047	Computer Science and Engineering (CSE)	First Year	SC	Male	2006-08-05	0000000000 (dummy)	student047.cse1@example.com	2026	Yavatmal	79.6	9.44	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-048	Rohan Desai	SAMPLE-2026-CSE-048	Computer Science and Engineering (CSE)	First Year	NT-D	Male	2006-02-08	0000000000 (dummy)	student048.cse1@example.com	2026	Buldhana	65.7	8.43	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-049	Shreyas Thakre	SAMPLE-2026-CSE-049	Computer Science and Engineering (CSE)	First Year	OPEN	Male	2006-10-04	0000000000 (dummy)	student049.cse1@example.com	2026	Nagpur	97.2	9.32	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-050	Ira Kamble	SAMPLE-2026-CSE-050	Computer Science and Engineering (CSE)	First Year	NT-C	Female	2006-03-27	0000000000 (dummy)	student050.cse1@example.com	2026	Chandrapur	80.3	9.39	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-051	Sneha Dange	SAMPLE-2026-CSE-051	Computer Science and Engineering (CSE)	First Year	SC	Female	2006-01-31	0000000000 (dummy)	student051.cse1@example.com	2026	Nashik	62.1	7.26	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-052	Gauri Gawande	SAMPLE-2026-CSE-052	Computer Science and Engineering (CSE)	First Year	VJ/DT	Female	2006-08-21	0000000000 (dummy)	student052.cse1@example.com	2026	Nashik	88.5	8.79	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-053	Saurabh Dawande	SAMPLE-2026-CSE-053	Computer Science and Engineering (CSE)	First Year	NT-D	Male	2006-10-12	0000000000 (dummy)	student053.cse1@example.com	2026	Akola	69.2	6.48	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-054	Tanvi Shaikh	SAMPLE-2026-CSE-054	Computer Science and Engineering (CSE)	First Year	EWS	Female	2006-01-30	0000000000 (dummy)	student054.cse1@example.com	2026	Jalgaon	82.6	8.87	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-055	Mrunal Pund	SAMPLE-2026-CSE-055	Computer Science and Engineering (CSE)	First Year	OPEN	Female	2006-01-30	0000000000 (dummy)	student055.cse1@example.com	2026	Washim	80.1	9.64	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-056	Ishaan Nimje	SAMPLE-2026-CSE-056	Computer Science and Engineering (CSE)	First Year	SC	Male	2006-09-29	0000000000 (dummy)	student056.cse1@example.com	2026	Amravati	98.5	5.86	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-057	Vedant Khan	SAMPLE-2026-CSE-057	Computer Science and Engineering (CSE)	First Year	OBC	Male	2006-04-06	0000000000 (dummy)	student057.cse1@example.com	2026	Washim	64.6	9.38	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-058	Akash Chavan	SAMPLE-2026-CSE-058	Computer Science and Engineering (CSE)	First Year	OBC	Male	2006-07-26	0000000000 (dummy)	student058.cse1@example.com	2026	Washim	71.4	8.18	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-059	Ishita Bhoyar	SAMPLE-2026-CSE-059	Computer Science and Engineering (CSE)	First Year	OBC	Female	2006-11-14	0000000000 (dummy)	student059.cse1@example.com	2026	Nashik	87	8.04	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE1-060	Sakshi Rathod	SAMPLE-2026-CSE-060	Computer Science and Engineering (CSE)	First Year	VJ/DT	Female	2006-06-11	0000000000 (dummy)	student060.cse1@example.com	2026	Wardha	87.4	6.91	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-001	Pooja Nimje	SAMPLE-2025-CSE-001	Computer Science and Engineering (CSE)	Second Year	NT-C	Female	2005-05-16	0000000000 (dummy)	student001.cse2@example.com	2025	Akola	87.5	6.85	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-002	Vaishnavi Khan	SAMPLE-2025-CSE-002	Computer Science and Engineering (CSE)	Second Year	OBC	Female	2005-06-11	0000000000 (dummy)	student002.cse2@example.com	2025	Amravati	79.4	9.99	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-003	Rahul Chavan	SAMPLE-2025-CSE-003	Computer Science and Engineering (CSE)	Second Year	OBC	Male	2005-02-21	0000000000 (dummy)	student003.cse2@example.com	2025	Buldhana	70.1	6.69	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-004	Simran Bhoyar	SAMPLE-2025-CSE-004	Computer Science and Engineering (CSE)	Second Year	OBC	Female	2005-06-28	0000000000 (dummy)	student004.cse2@example.com	2025	Wardha	76	6.21	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-005	Janvi Rathod	SAMPLE-2025-CSE-005	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Female	2005-10-06	0000000000 (dummy)	student005.cse2@example.com	2025	Washim	99.4	9.13	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-006	Sai Kadam	SAMPLE-2025-CSE-006	Computer Science and Engineering (CSE)	Second Year	OPEN	Male	2005-09-28	0000000000 (dummy)	student006.cse2@example.com	2025	Aurangabad	93	6.85	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-007	Om Dhole	SAMPLE-2025-CSE-007	Computer Science and Engineering (CSE)	Second Year	OBC	Male	2005-12-06	0000000000 (dummy)	student007.cse2@example.com	2025	Akola	72	9.5	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-008	Nikhil Tiwari	SAMPLE-2025-CSE-008	Computer Science and Engineering (CSE)	Second Year	SC	Male	2005-10-11	0000000000 (dummy)	student008.cse2@example.com	2025	Yavatmal	72.7	6.45	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-009	Myra More	SAMPLE-2025-CSE-009	Computer Science and Engineering (CSE)	Second Year	ST	Female	2005-06-25	0000000000 (dummy)	student009.cse2@example.com	2025	Aurangabad	86.1	6.69	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-010	Priya Mahajan	SAMPLE-2025-CSE-010	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Female	2005-09-08	0000000000 (dummy)	student010.cse2@example.com	2025	Amravati	65.5	7.41	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-011	Nandini Singh	SAMPLE-2025-CSE-011	Computer Science and Engineering (CSE)	Second Year	OPEN	Female	2005-05-22	0000000000 (dummy)	student011.cse2@example.com	2025	Amravati	74.7	6.09	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-012	Parth Jadhav	SAMPLE-2025-CSE-012	Computer Science and Engineering (CSE)	Second Year	SC	Male	2005-05-15	0000000000 (dummy)	student012.cse2@example.com	2025	Jalgaon	78.8	8.68	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-013	Shreya Borkar	SAMPLE-2025-CSE-013	Computer Science and Engineering (CSE)	Second Year	OPEN	Female	2005-10-15	0000000000 (dummy)	student013.cse2@example.com	2025	Nagpur	64.9	9.47	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-014	Aarav Yadav	SAMPLE-2025-CSE-014	Computer Science and Engineering (CSE)	Second Year	SBC	Male	2005-03-18	0000000000 (dummy)	student014.cse2@example.com	2025	Amravati	93.7	8.12	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-015	Atharv Kulkarni	SAMPLE-2025-CSE-015	Computer Science and Engineering (CSE)	Second Year	NT-C	Male	2005-03-17	0000000000 (dummy)	student015.cse2@example.com	2025	Akola	63.6	7.14	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-016	Pranav Kale	SAMPLE-2025-CSE-016	Computer Science and Engineering (CSE)	Second Year	NT-B	Male	2005-01-21	0000000000 (dummy)	student016.cse2@example.com	2025	Wardha	87.9	8.5	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-017	Aditi Sharma	SAMPLE-2025-CSE-017	Computer Science and Engineering (CSE)	Second Year	SBC	Female	2005-07-01	0000000000 (dummy)	student017.cse2@example.com	2025	Nashik	99	8.87	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-018	Riya Joshi	SAMPLE-2025-CSE-018	Computer Science and Engineering (CSE)	Second Year	SC	Female	2005-05-02	0000000000 (dummy)	student018.cse2@example.com	2025	Akola	95.5	5.61	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-019	Mansi Ingole	SAMPLE-2025-CSE-019	Computer Science and Engineering (CSE)	Second Year	NT-C	Female	2005-06-20	0000000000 (dummy)	student019.cse2@example.com	2025	Aurangabad	94.8	9.15	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-020	Abhishek Gupta	SAMPLE-2025-CSE-020	Computer Science and Engineering (CSE)	Second Year	SC	Male	2005-05-17	0000000000 (dummy)	student020.cse2@example.com	2025	Jalgaon	66.1	9.42	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-021	Tejas Shinde	SAMPLE-2025-CSE-021	Computer Science and Engineering (CSE)	Second Year	ST	Male	2005-08-29	0000000000 (dummy)	student021.cse2@example.com	2025	Wardha	93	7.57	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-022	Rutuja Mankar	SAMPLE-2025-CSE-022	Computer Science and Engineering (CSE)	Second Year	ST	Female	2005-06-06	0000000000 (dummy)	student022.cse2@example.com	2025	Wardha	62.9	6.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-023	Arjun Verma	SAMPLE-2025-CSE-023	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Male	2005-06-18	0000000000 (dummy)	student023.cse2@example.com	2025	Nagpur	98.7	6.76	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-024	Siddharth Pawar	SAMPLE-2025-CSE-024	Computer Science and Engineering (CSE)	Second Year	SBC	Male	2005-11-25	0000000000 (dummy)	student024.cse2@example.com	2025	Nashik	87.8	9.3	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-025	Kunal Raut	SAMPLE-2025-CSE-025	Computer Science and Engineering (CSE)	Second Year	OPEN	Male	2005-06-19	0000000000 (dummy)	student025.cse2@example.com	2025	Nagpur	95.3	6.68	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-026	Diya Mishra	SAMPLE-2025-CSE-026	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Female	2005-10-25	0000000000 (dummy)	student026.cse2@example.com	2025	Amravati	66.1	7.46	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-027	Neha Deshmukh	SAMPLE-2025-CSE-027	Computer Science and Engineering (CSE)	Second Year	NT-C	Female	2005-06-10	0000000000 (dummy)	student027.cse2@example.com	2025	Washim	99.4	6.02	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-028	Trisha Wankhede	SAMPLE-2025-CSE-028	Computer Science and Engineering (CSE)	Second Year	ST	Female	2005-10-23	0000000000 (dummy)	student028.cse2@example.com	2025	Yavatmal	63.7	7.46	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-029	Chaitanya Suryawanshi	SAMPLE-2025-CSE-029	Computer Science and Engineering (CSE)	Second Year	SBC	Male	2005-09-24	0000000000 (dummy)	student029.cse2@example.com	2025	Aurangabad	89.3	8.84	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-030	Prachi Patil	SAMPLE-2025-CSE-030	Computer Science and Engineering (CSE)	Second Year	ST	Female	2005-12-10	0000000000 (dummy)	student030.cse2@example.com	2025	Pune	78.4	9.77	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-031	Anushka Bansod	SAMPLE-2025-CSE-031	Computer Science and Engineering (CSE)	Second Year	EWS	Female	2005-06-19	0000000000 (dummy)	student031.cse2@example.com	2025	Pune	87.2	6.06	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-032	Reyansh Gaikwad	SAMPLE-2025-CSE-032	Computer Science and Engineering (CSE)	Second Year	SBC	Male	2005-06-03	0000000000 (dummy)	student032.cse2@example.com	2025	Yavatmal	87.3	6.97	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-033	Yash Desai	SAMPLE-2025-CSE-033	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Male	2005-12-23	0000000000 (dummy)	student033.cse2@example.com	2025	Buldhana	66.8	7.39	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-034	Ananya Thakre	SAMPLE-2025-CSE-034	Computer Science and Engineering (CSE)	Second Year	SC	Female	2005-07-14	0000000000 (dummy)	student034.cse2@example.com	2025	Washim	83.6	7.33	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-035	Kavya Kamble	SAMPLE-2025-CSE-035	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Female	2005-01-01	0000000000 (dummy)	student035.cse2@example.com	2025	Yavatmal	70	9.04	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-036	Shruti Dange	SAMPLE-2025-CSE-036	Computer Science and Engineering (CSE)	Second Year	NT-B	Female	2005-11-07	0000000000 (dummy)	student036.cse2@example.com	2025	Chandrapur	78.8	8.54	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-037	Harsh Gawande	SAMPLE-2025-CSE-037	Computer Science and Engineering (CSE)	Second Year	NT-D	Male	2005-09-19	0000000000 (dummy)	student037.cse2@example.com	2025	Jalgaon	68.4	5.88	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-038	Dev Dawande	SAMPLE-2025-CSE-038	Computer Science and Engineering (CSE)	Second Year	EWS	Male	2005-09-21	0000000000 (dummy)	student038.cse2@example.com	2025	Pune	65.5	9.78	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-039	Komal Shaikh	SAMPLE-2025-CSE-039	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Female	2005-05-01	0000000000 (dummy)	student039.cse2@example.com	2025	Wardha	92.6	6.16	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-040	Aditya Pund	SAMPLE-2025-CSE-040	Computer Science and Engineering (CSE)	Second Year	ST	Male	2005-01-24	0000000000 (dummy)	student040.cse2@example.com	2025	Chandrapur	85.2	8.96	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-041	Rohan Nimje	SAMPLE-2025-CSE-041	Computer Science and Engineering (CSE)	Second Year	NT-C	Male	2005-08-22	0000000000 (dummy)	student041.cse2@example.com	2025	Aurangabad	83.9	8.73	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-042	Shreyas Khan	SAMPLE-2025-CSE-042	Computer Science and Engineering (CSE)	Second Year	NT-D	Male	2005-07-16	0000000000 (dummy)	student042.cse2@example.com	2025	Nashik	71.3	8.45	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-043	Ira Chavan	SAMPLE-2025-CSE-043	Computer Science and Engineering (CSE)	Second Year	OBC	Female	2005-01-03	0000000000 (dummy)	student043.cse2@example.com	2025	Nashik	70.3	9.12	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-044	Sneha Bhoyar	SAMPLE-2025-CSE-044	Computer Science and Engineering (CSE)	Second Year	SBC	Female	2005-12-23	0000000000 (dummy)	student044.cse2@example.com	2025	Chandrapur	63.9	6.62	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-045	Gauri Rathod	SAMPLE-2025-CSE-045	Computer Science and Engineering (CSE)	Second Year	NT-D	Female	2005-03-04	0000000000 (dummy)	student045.cse2@example.com	2025	Akola	92.5	8.5	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-046	Saurabh Kadam	SAMPLE-2025-CSE-046	Computer Science and Engineering (CSE)	Second Year	EWS	Male	2005-10-14	0000000000 (dummy)	student046.cse2@example.com	2025	Pune	98.1	9.51	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-047	Tanvi Dhole	SAMPLE-2025-CSE-047	Computer Science and Engineering (CSE)	Second Year	SBC	Female	2005-11-10	0000000000 (dummy)	student047.cse2@example.com	2025	Nashik	93.6	7.97	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-048	Mrunal Tiwari	SAMPLE-2025-CSE-048	Computer Science and Engineering (CSE)	Second Year	NT-D	Female	2005-03-23	0000000000 (dummy)	student048.cse2@example.com	2025	Chandrapur	71.8	6.61	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-049	Ishaan More	SAMPLE-2025-CSE-049	Computer Science and Engineering (CSE)	Second Year	VJ/DT	Male	2005-11-23	0000000000 (dummy)	student049.cse2@example.com	2025	Buldhana	80.4	6.58	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-050	Vedant Mahajan	SAMPLE-2025-CSE-050	Computer Science and Engineering (CSE)	Second Year	OBC	Male	2005-08-14	0000000000 (dummy)	student050.cse2@example.com	2025	Jalgaon	72.9	6.72	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-051	Akash Singh	SAMPLE-2025-CSE-051	Computer Science and Engineering (CSE)	Second Year	SBC	Male	2005-06-13	0000000000 (dummy)	student051.cse2@example.com	2025	Nagpur	67.3	6.54	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-052	Ishita Jadhav	SAMPLE-2025-CSE-052	Computer Science and Engineering (CSE)	Second Year	SC	Female	2005-12-22	0000000000 (dummy)	student052.cse2@example.com	2025	Jalgaon	70.1	7.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-053	Sakshi Borkar	SAMPLE-2025-CSE-053	Computer Science and Engineering (CSE)	Second Year	SBC	Female	2005-06-19	0000000000 (dummy)	student053.cse2@example.com	2025	Chandrapur	77.8	6.43	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-054	Manav Yadav	SAMPLE-2025-CSE-054	Computer Science and Engineering (CSE)	Second Year	NT-C	Male	2005-08-04	0000000000 (dummy)	student054.cse2@example.com	2025	Washim	98	5.59	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-055	Ayush Kulkarni	SAMPLE-2025-CSE-055	Computer Science and Engineering (CSE)	Second Year	NT-C	Male	2005-10-22	0000000000 (dummy)	student055.cse2@example.com	2025	Chandrapur	62.2	7.08	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-056	Amruta Kale	SAMPLE-2025-CSE-056	Computer Science and Engineering (CSE)	Second Year	NT-C	Female	2005-07-19	0000000000 (dummy)	student056.cse2@example.com	2025	Buldhana	90.4	7.96	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-057	Vivaan Sharma	SAMPLE-2025-CSE-057	Computer Science and Engineering (CSE)	Second Year	ST	Male	2005-11-05	0000000000 (dummy)	student057.cse2@example.com	2025	Chandrapur	70.3	7.46	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-058	Krishna Joshi	SAMPLE-2025-CSE-058	Computer Science and Engineering (CSE)	Second Year	NT-C	Male	2005-01-15	0000000000 (dummy)	student058.cse2@example.com	2025	Pune	87.4	9.09	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-059	Tanmay Ingole	SAMPLE-2025-CSE-059	Computer Science and Engineering (CSE)	Second Year	NT-D	Male	2005-03-26	0000000000 (dummy)	student059.cse2@example.com	2025	Akola	99.3	7.9	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE2-060	Saanvi Gupta	SAMPLE-2025-CSE-060	Computer Science and Engineering (CSE)	Second Year	EWS	Female	2005-07-21	0000000000 (dummy)	student060.cse2@example.com	2025	Washim	87.2	5.88	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-001	Nikhil Kale	SAMPLE-2024-CSE-001	Computer Science and Engineering (CSE)	Third Year	SC	Male	2004-08-07	0000000000 (dummy)	student001.cse3@example.com	2024	Chandrapur	68.9	6.67	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-002	Myra Sharma	SAMPLE-2024-CSE-002	Computer Science and Engineering (CSE)	Third Year	ST	Female	2004-06-16	0000000000 (dummy)	student002.cse3@example.com	2024	Chandrapur	74.4	8.93	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-003	Priya Joshi	SAMPLE-2024-CSE-003	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Female	2004-07-13	0000000000 (dummy)	student003.cse3@example.com	2024	Nashik	71.6	5.87	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-004	Nandini Ingole	SAMPLE-2024-CSE-004	Computer Science and Engineering (CSE)	Third Year	SBC	Female	2004-01-10	0000000000 (dummy)	student004.cse3@example.com	2024	Amravati	100	7.07	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-005	Parth Gupta	SAMPLE-2024-CSE-005	Computer Science and Engineering (CSE)	Third Year	OBC	Male	2004-11-28	0000000000 (dummy)	student005.cse3@example.com	2024	Aurangabad	63.5	5.64	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-006	Shreya Shinde	SAMPLE-2024-CSE-006	Computer Science and Engineering (CSE)	Third Year	ST	Female	2004-05-06	0000000000 (dummy)	student006.cse3@example.com	2024	Amravati	85.6	6.57	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-007	Aarav Mankar	SAMPLE-2024-CSE-007	Computer Science and Engineering (CSE)	Third Year	OBC	Male	2004-08-30	0000000000 (dummy)	student007.cse3@example.com	2024	Washim	98	7.59	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-008	Atharv Verma	SAMPLE-2024-CSE-008	Computer Science and Engineering (CSE)	Third Year	NT-B	Male	2004-05-11	0000000000 (dummy)	student008.cse3@example.com	2024	Akola	85	9.84	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-009	Pranav Pawar	SAMPLE-2024-CSE-009	Computer Science and Engineering (CSE)	Third Year	SC	Male	2004-02-28	0000000000 (dummy)	student009.cse3@example.com	2024	Yavatmal	66.1	5.62	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-010	Aditi Raut	SAMPLE-2024-CSE-010	Computer Science and Engineering (CSE)	Third Year	EWS	Female	2004-06-08	0000000000 (dummy)	student010.cse3@example.com	2024	Aurangabad	96.5	7.19	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-011	Riya Mishra	SAMPLE-2024-CSE-011	Computer Science and Engineering (CSE)	Third Year	OBC	Female	2004-04-11	0000000000 (dummy)	student011.cse3@example.com	2024	Washim	88.2	8.32	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-012	Mansi Deshmukh	SAMPLE-2024-CSE-012	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Female	2004-02-22	0000000000 (dummy)	student012.cse3@example.com	2024	Aurangabad	84.8	6.04	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-013	Abhishek Wankhede	SAMPLE-2024-CSE-013	Computer Science and Engineering (CSE)	Third Year	OPEN	Male	2004-10-16	0000000000 (dummy)	student013.cse3@example.com	2024	Pune	82.2	8.48	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-014	Tejas Suryawanshi	SAMPLE-2024-CSE-014	Computer Science and Engineering (CSE)	Third Year	SBC	Male	2004-02-05	0000000000 (dummy)	student014.cse3@example.com	2024	Aurangabad	75	9.32	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-015	Rutuja Patil	SAMPLE-2024-CSE-015	Computer Science and Engineering (CSE)	Third Year	OBC	Female	2004-09-07	0000000000 (dummy)	student015.cse3@example.com	2024	Nashik	98.5	8.36	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-016	Arjun Bansod	SAMPLE-2024-CSE-016	Computer Science and Engineering (CSE)	Third Year	SC	Male	2004-08-23	0000000000 (dummy)	student016.cse3@example.com	2024	Nashik	68.7	7.85	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-017	Siddharth Gaikwad	SAMPLE-2024-CSE-017	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Male	2004-11-29	0000000000 (dummy)	student017.cse3@example.com	2024	Washim	92.7	7.92	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-018	Kunal Desai	SAMPLE-2024-CSE-018	Computer Science and Engineering (CSE)	Third Year	NT-D	Male	2004-09-04	0000000000 (dummy)	student018.cse3@example.com	2024	Nashik	93.4	8.17	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-019	Diya Thakre	SAMPLE-2024-CSE-019	Computer Science and Engineering (CSE)	Third Year	ST	Female	2004-06-14	0000000000 (dummy)	student019.cse3@example.com	2024	Nagpur	72.6	7.53	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-020	Neha Kamble	SAMPLE-2024-CSE-020	Computer Science and Engineering (CSE)	Third Year	EWS	Female	2004-08-25	0000000000 (dummy)	student020.cse3@example.com	2024	Washim	87.4	7.01	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-021	Trisha Dange	SAMPLE-2024-CSE-021	Computer Science and Engineering (CSE)	Third Year	NT-B	Female	2004-09-10	0000000000 (dummy)	student021.cse3@example.com	2024	Akola	80.5	7.1	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-022	Chaitanya Gawande	SAMPLE-2024-CSE-022	Computer Science and Engineering (CSE)	Third Year	NT-B	Male	2004-05-12	0000000000 (dummy)	student022.cse3@example.com	2024	Yavatmal	95.5	8.66	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-023	Prachi Dawande	SAMPLE-2024-CSE-023	Computer Science and Engineering (CSE)	Third Year	SBC	Female	2004-05-21	0000000000 (dummy)	student023.cse3@example.com	2024	Amravati	81.6	6.36	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-024	Anushka Shaikh	SAMPLE-2024-CSE-024	Computer Science and Engineering (CSE)	Third Year	NT-C	Female	2004-05-03	0000000000 (dummy)	student024.cse3@example.com	2024	Chandrapur	83.1	6.58	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-025	Reyansh Pund	SAMPLE-2024-CSE-025	Computer Science and Engineering (CSE)	Third Year	NT-D	Male	2004-08-31	0000000000 (dummy)	student025.cse3@example.com	2024	Chandrapur	92.1	5.92	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-026	Yash Nimje	SAMPLE-2024-CSE-026	Computer Science and Engineering (CSE)	Third Year	NT-C	Male	2004-04-23	0000000000 (dummy)	student026.cse3@example.com	2024	Jalgaon	71.2	8.49	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-027	Ananya Khan	SAMPLE-2024-CSE-027	Computer Science and Engineering (CSE)	Third Year	NT-D	Female	2004-07-07	0000000000 (dummy)	student027.cse3@example.com	2024	Buldhana	82.2	7.41	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-028	Kavya Chavan	SAMPLE-2024-CSE-028	Computer Science and Engineering (CSE)	Third Year	NT-B	Female	2004-10-08	0000000000 (dummy)	student028.cse3@example.com	2024	Pune	88.7	6.72	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-029	Shruti Bhoyar	SAMPLE-2024-CSE-029	Computer Science and Engineering (CSE)	Third Year	ST	Female	2004-05-08	0000000000 (dummy)	student029.cse3@example.com	2024	Nagpur	89.4	6.92	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-030	Harsh Rathod	SAMPLE-2024-CSE-030	Computer Science and Engineering (CSE)	Third Year	SC	Male	2004-10-01	0000000000 (dummy)	student030.cse3@example.com	2024	Wardha	70.2	7.68	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-031	Dev Kadam	SAMPLE-2024-CSE-031	Computer Science and Engineering (CSE)	Third Year	SBC	Male	2004-10-28	0000000000 (dummy)	student031.cse3@example.com	2024	Washim	72.8	5.95	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-032	Komal Dhole	SAMPLE-2024-CSE-032	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Female	2004-04-09	0000000000 (dummy)	student032.cse3@example.com	2024	Wardha	75.7	6.86	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-033	Aditya Tiwari	SAMPLE-2024-CSE-033	Computer Science and Engineering (CSE)	Third Year	SBC	Male	2004-12-28	0000000000 (dummy)	student033.cse3@example.com	2024	Akola	72.4	9.88	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-034	Rohan More	SAMPLE-2024-CSE-034	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Male	2004-10-10	0000000000 (dummy)	student034.cse3@example.com	2024	Jalgaon	97.9	8.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-035	Shreyas Mahajan	SAMPLE-2024-CSE-035	Computer Science and Engineering (CSE)	Third Year	OBC	Male	2004-09-08	0000000000 (dummy)	student035.cse3@example.com	2024	Amravati	83.8	7.61	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-036	Ira Singh	SAMPLE-2024-CSE-036	Computer Science and Engineering (CSE)	Third Year	NT-B	Female	2004-08-13	0000000000 (dummy)	student036.cse3@example.com	2024	Akola	98.7	6.64	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-037	Sneha Jadhav	SAMPLE-2024-CSE-037	Computer Science and Engineering (CSE)	Third Year	OBC	Female	2004-09-01	0000000000 (dummy)	student037.cse3@example.com	2024	Nagpur	77.2	5.83	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-038	Gauri Borkar	SAMPLE-2024-CSE-038	Computer Science and Engineering (CSE)	Third Year	OPEN	Female	2004-11-18	0000000000 (dummy)	student038.cse3@example.com	2024	Akola	67.7	8.03	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-039	Saurabh Yadav	SAMPLE-2024-CSE-039	Computer Science and Engineering (CSE)	Third Year	OBC	Male	2004-06-04	0000000000 (dummy)	student039.cse3@example.com	2024	Wardha	66.5	8.94	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-040	Tanvi Kulkarni	SAMPLE-2024-CSE-040	Computer Science and Engineering (CSE)	Third Year	EWS	Female	2004-11-06	0000000000 (dummy)	student040.cse3@example.com	2024	Washim	70.6	7.85	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-041	Mrunal Kale	SAMPLE-2024-CSE-041	Computer Science and Engineering (CSE)	Third Year	NT-D	Female	2004-08-18	0000000000 (dummy)	student041.cse3@example.com	2024	Yavatmal	94.7	9.96	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-042	Ishaan Sharma	SAMPLE-2024-CSE-042	Computer Science and Engineering (CSE)	Third Year	EWS	Male	2004-06-05	0000000000 (dummy)	student042.cse3@example.com	2024	Washim	64.3	9.82	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-043	Vedant Joshi	SAMPLE-2024-CSE-043	Computer Science and Engineering (CSE)	Third Year	ST	Male	2004-02-20	0000000000 (dummy)	student043.cse3@example.com	2024	Aurangabad	70	8.47	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-044	Akash Ingole	SAMPLE-2024-CSE-044	Computer Science and Engineering (CSE)	Third Year	ST	Male	2004-03-21	0000000000 (dummy)	student044.cse3@example.com	2024	Akola	83	6.2	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-045	Ishita Gupta	SAMPLE-2024-CSE-045	Computer Science and Engineering (CSE)	Third Year	NT-D	Female	2004-07-28	0000000000 (dummy)	student045.cse3@example.com	2024	Jalgaon	84.6	6.81	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-046	Sakshi Shinde	SAMPLE-2024-CSE-046	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Female	2004-04-28	0000000000 (dummy)	student046.cse3@example.com	2024	Jalgaon	72.7	9.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-047	Manav Mankar	SAMPLE-2024-CSE-047	Computer Science and Engineering (CSE)	Third Year	ST	Male	2004-02-06	0000000000 (dummy)	student047.cse3@example.com	2024	Yavatmal	91.9	8.31	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-048	Ayush Verma	SAMPLE-2024-CSE-048	Computer Science and Engineering (CSE)	Third Year	ST	Male	2004-12-04	0000000000 (dummy)	student048.cse3@example.com	2024	Nashik	66.4	6.51	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-049	Amruta Pawar	SAMPLE-2024-CSE-049	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Female	2004-03-17	0000000000 (dummy)	student049.cse3@example.com	2024	Akola	64.7	6.25	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-050	Vivaan Raut	SAMPLE-2024-CSE-050	Computer Science and Engineering (CSE)	Third Year	EWS	Male	2004-06-06	0000000000 (dummy)	student050.cse3@example.com	2024	Jalgaon	93.3	9.65	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-051	Krishna Mishra	SAMPLE-2024-CSE-051	Computer Science and Engineering (CSE)	Third Year	OBC	Male	2004-08-12	0000000000 (dummy)	student051.cse3@example.com	2024	Chandrapur	88.2	8.65	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-052	Tanmay Deshmukh	SAMPLE-2024-CSE-052	Computer Science and Engineering (CSE)	Third Year	SBC	Male	2004-05-19	0000000000 (dummy)	student052.cse3@example.com	2024	Buldhana	80.8	5.86	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-053	Saanvi Wankhede	SAMPLE-2024-CSE-053	Computer Science and Engineering (CSE)	Third Year	NT-C	Female	2004-01-21	0000000000 (dummy)	student053.cse3@example.com	2024	Jalgaon	74.2	6.63	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-054	Pooja Suryawanshi	SAMPLE-2024-CSE-054	Computer Science and Engineering (CSE)	Third Year	ST	Female	2004-02-16	0000000000 (dummy)	student054.cse3@example.com	2024	Aurangabad	93.8	8.09	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-055	Vaishnavi Patil	SAMPLE-2024-CSE-055	Computer Science and Engineering (CSE)	Third Year	VJ/DT	Female	2004-01-11	0000000000 (dummy)	student055.cse3@example.com	2024	Washim	63.5	8.9	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-056	Rahul Bansod	SAMPLE-2024-CSE-056	Computer Science and Engineering (CSE)	Third Year	SBC	Male	2004-08-28	0000000000 (dummy)	student056.cse3@example.com	2024	Aurangabad	78.8	6.75	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-057	Simran Gaikwad	SAMPLE-2024-CSE-057	Computer Science and Engineering (CSE)	Third Year	NT-C	Female	2004-10-26	0000000000 (dummy)	student057.cse3@example.com	2024	Aurangabad	92.9	9.86	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-058	Janvi Desai	SAMPLE-2024-CSE-058	Computer Science and Engineering (CSE)	Third Year	NT-B	Female	2004-08-28	0000000000 (dummy)	student058.cse3@example.com	2024	Nashik	74.7	8.52	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-059	Sai Thakre	SAMPLE-2024-CSE-059	Computer Science and Engineering (CSE)	Third Year	NT-B	Male	2004-03-23	0000000000 (dummy)	student059.cse3@example.com	2024	Nashik	88.4	6.8	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE3-060	Om Kamble	SAMPLE-2024-CSE-060	Computer Science and Engineering (CSE)	Third Year	SBC	Male	2004-07-24	0000000000 (dummy)	student060.cse3@example.com	2024	Amravati	79.3	6.92	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-001	Atharv Bansod	SAMPLE-2023-CSE-001	Computer Science and Engineering (CSE)	Final Year	OBC	Male	2003-06-15	0000000000 (dummy)	student001.cse4@example.com	2023	Nashik	94.9	9.21	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-002	Pranav Gaikwad	SAMPLE-2023-CSE-002	Computer Science and Engineering (CSE)	Final Year	SBC	Male	2003-01-01	0000000000 (dummy)	student002.cse4@example.com	2023	Chandrapur	77.7	6.34	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-003	Aditi Desai	SAMPLE-2023-CSE-003	Computer Science and Engineering (CSE)	Final Year	EWS	Female	2003-07-05	0000000000 (dummy)	student003.cse4@example.com	2023	Chandrapur	85.8	8.92	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-004	Riya Thakre	SAMPLE-2023-CSE-004	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Female	2003-04-15	0000000000 (dummy)	student004.cse4@example.com	2023	Buldhana	67	6.8	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-005	Mansi Kamble	SAMPLE-2023-CSE-005	Computer Science and Engineering (CSE)	Final Year	NT-D	Female	2003-12-24	0000000000 (dummy)	student005.cse4@example.com	2023	Nagpur	63.1	8.34	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-006	Abhishek Dange	SAMPLE-2023-CSE-006	Computer Science and Engineering (CSE)	Final Year	SC	Male	2003-05-03	0000000000 (dummy)	student006.cse4@example.com	2023	Yavatmal	82.9	7.99	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-007	Tejas Gawande	SAMPLE-2023-CSE-007	Computer Science and Engineering (CSE)	Final Year	ST	Male	2003-02-17	0000000000 (dummy)	student007.cse4@example.com	2023	Nagpur	79.5	6.03	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-008	Rutuja Dawande	SAMPLE-2023-CSE-008	Computer Science and Engineering (CSE)	Final Year	NT-D	Female	2003-03-20	0000000000 (dummy)	student008.cse4@example.com	2023	Jalgaon	73.1	8.67	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-009	Arjun Shaikh	SAMPLE-2023-CSE-009	Computer Science and Engineering (CSE)	Final Year	NT-D	Male	2003-08-01	0000000000 (dummy)	student009.cse4@example.com	2023	Chandrapur	71.3	7.98	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-010	Siddharth Pund	SAMPLE-2023-CSE-010	Computer Science and Engineering (CSE)	Final Year	ST	Male	2003-07-16	0000000000 (dummy)	student010.cse4@example.com	2023	Washim	81.3	9.46	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-011	Kunal Nimje	SAMPLE-2023-CSE-011	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Male	2003-02-05	0000000000 (dummy)	student011.cse4@example.com	2023	Nashik	74.9	9.04	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-012	Diya Khan	SAMPLE-2023-CSE-012	Computer Science and Engineering (CSE)	Final Year	OPEN	Female	2003-05-17	0000000000 (dummy)	student012.cse4@example.com	2023	Yavatmal	89.6	9.27	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-013	Neha Chavan	SAMPLE-2023-CSE-013	Computer Science and Engineering (CSE)	Final Year	NT-D	Female	2003-10-24	0000000000 (dummy)	student013.cse4@example.com	2023	Akola	79	7.68	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-014	Trisha Bhoyar	SAMPLE-2023-CSE-014	Computer Science and Engineering (CSE)	Final Year	SBC	Female	2003-06-20	0000000000 (dummy)	student014.cse4@example.com	2023	Buldhana	76.3	9.7	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-015	Chaitanya Rathod	SAMPLE-2023-CSE-015	Computer Science and Engineering (CSE)	Final Year	ST	Male	2003-04-07	0000000000 (dummy)	student015.cse4@example.com	2023	Washim	76.6	9.35	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-016	Prachi Kadam	SAMPLE-2023-CSE-016	Computer Science and Engineering (CSE)	Final Year	OPEN	Female	2003-07-30	0000000000 (dummy)	student016.cse4@example.com	2023	Pune	90.3	8.67	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-017	Anushka Dhole	SAMPLE-2023-CSE-017	Computer Science and Engineering (CSE)	Final Year	NT-C	Female	2003-07-15	0000000000 (dummy)	student017.cse4@example.com	2023	Aurangabad	92.1	8.43	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-018	Reyansh Tiwari	SAMPLE-2023-CSE-018	Computer Science and Engineering (CSE)	Final Year	NT-D	Male	2003-03-19	0000000000 (dummy)	student018.cse4@example.com	2023	Amravati	66.8	9.84	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-019	Yash More	SAMPLE-2023-CSE-019	Computer Science and Engineering (CSE)	Final Year	OBC	Male	2003-06-19	0000000000 (dummy)	student019.cse4@example.com	2023	Chandrapur	65.8	9.6	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-020	Ananya Mahajan	SAMPLE-2023-CSE-020	Computer Science and Engineering (CSE)	Final Year	SC	Female	2003-01-08	0000000000 (dummy)	student020.cse4@example.com	2023	Nashik	95.1	9.86	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-021	Kavya Singh	SAMPLE-2023-CSE-021	Computer Science and Engineering (CSE)	Final Year	NT-D	Female	2003-02-08	0000000000 (dummy)	student021.cse4@example.com	2023	Yavatmal	74.9	8.62	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-022	Shruti Jadhav	SAMPLE-2023-CSE-022	Computer Science and Engineering (CSE)	Final Year	OBC	Female	2003-11-29	0000000000 (dummy)	student022.cse4@example.com	2023	Pune	94.4	9.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-023	Harsh Borkar	SAMPLE-2023-CSE-023	Computer Science and Engineering (CSE)	Final Year	NT-B	Male	2003-07-14	0000000000 (dummy)	student023.cse4@example.com	2023	Aurangabad	89.3	8.92	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-024	Dev Yadav	SAMPLE-2023-CSE-024	Computer Science and Engineering (CSE)	Final Year	OPEN	Male	2003-10-05	0000000000 (dummy)	student024.cse4@example.com	2023	Washim	64.6	8.34	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-025	Komal Kulkarni	SAMPLE-2023-CSE-025	Computer Science and Engineering (CSE)	Final Year	ST	Female	2003-05-28	0000000000 (dummy)	student025.cse4@example.com	2023	Jalgaon	65.4	9.9	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-026	Aditya Kale	SAMPLE-2023-CSE-026	Computer Science and Engineering (CSE)	Final Year	OBC	Male	2003-11-21	0000000000 (dummy)	student026.cse4@example.com	2023	Chandrapur	68.3	6.85	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-027	Rohan Sharma	SAMPLE-2023-CSE-027	Computer Science and Engineering (CSE)	Final Year	OPEN	Male	2003-01-15	0000000000 (dummy)	student027.cse4@example.com	2023	Pune	92.3	6.82	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-028	Shreyas Joshi	SAMPLE-2023-CSE-028	Computer Science and Engineering (CSE)	Final Year	NT-C	Male	2003-07-11	0000000000 (dummy)	student028.cse4@example.com	2023	Akola	71.3	7.35	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-029	Ira Ingole	SAMPLE-2023-CSE-029	Computer Science and Engineering (CSE)	Final Year	SC	Female	2003-12-16	0000000000 (dummy)	student029.cse4@example.com	2023	Akola	68.7	8.24	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-030	Sneha Gupta	SAMPLE-2023-CSE-030	Computer Science and Engineering (CSE)	Final Year	EWS	Female	2003-07-15	0000000000 (dummy)	student030.cse4@example.com	2023	Aurangabad	71.2	9.61	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-031	Gauri Shinde	SAMPLE-2023-CSE-031	Computer Science and Engineering (CSE)	Final Year	ST	Female	2003-03-15	0000000000 (dummy)	student031.cse4@example.com	2023	Chandrapur	86.2	7.57	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-032	Saurabh Mankar	SAMPLE-2023-CSE-032	Computer Science and Engineering (CSE)	Final Year	OPEN	Male	2003-12-08	0000000000 (dummy)	student032.cse4@example.com	2023	Chandrapur	96.2	8.55	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-033	Tanvi Verma	SAMPLE-2023-CSE-033	Computer Science and Engineering (CSE)	Final Year	OBC	Female	2003-03-22	0000000000 (dummy)	student033.cse4@example.com	2023	Chandrapur	97.9	9.94	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-034	Mrunal Pawar	SAMPLE-2023-CSE-034	Computer Science and Engineering (CSE)	Final Year	NT-C	Female	2003-06-03	0000000000 (dummy)	student034.cse4@example.com	2023	Jalgaon	71.5	9.3	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-035	Ishaan Raut	SAMPLE-2023-CSE-035	Computer Science and Engineering (CSE)	Final Year	NT-C	Male	2003-04-12	0000000000 (dummy)	student035.cse4@example.com	2023	Chandrapur	66.1	7.22	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-036	Vedant Mishra	SAMPLE-2023-CSE-036	Computer Science and Engineering (CSE)	Final Year	EWS	Male	2003-07-03	0000000000 (dummy)	student036.cse4@example.com	2023	Yavatmal	99.7	6.83	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-037	Akash Deshmukh	SAMPLE-2023-CSE-037	Computer Science and Engineering (CSE)	Final Year	NT-C	Male	2003-12-04	0000000000 (dummy)	student037.cse4@example.com	2023	Yavatmal	62.3	9.39	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-038	Ishita Wankhede	SAMPLE-2023-CSE-038	Computer Science and Engineering (CSE)	Final Year	EWS	Female	2003-01-26	0000000000 (dummy)	student038.cse4@example.com	2023	Jalgaon	80.9	9.57	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-039	Sakshi Suryawanshi	SAMPLE-2023-CSE-039	Computer Science and Engineering (CSE)	Final Year	ST	Female	2003-05-27	0000000000 (dummy)	student039.cse4@example.com	2023	Washim	92.5	6.49	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-040	Manav Patil	SAMPLE-2023-CSE-040	Computer Science and Engineering (CSE)	Final Year	EWS	Male	2003-04-08	0000000000 (dummy)	student040.cse4@example.com	2023	Yavatmal	87.8	8.74	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-041	Ayush Bansod	SAMPLE-2023-CSE-041	Computer Science and Engineering (CSE)	Final Year	SC	Male	2003-12-04	0000000000 (dummy)	student041.cse4@example.com	2023	Aurangabad	65.7	8.32	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-042	Amruta Gaikwad	SAMPLE-2023-CSE-042	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Female	2003-01-21	0000000000 (dummy)	student042.cse4@example.com	2023	Chandrapur	63.3	7.14	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-043	Vivaan Desai	SAMPLE-2023-CSE-043	Computer Science and Engineering (CSE)	Final Year	OBC	Male	2003-03-09	0000000000 (dummy)	student043.cse4@example.com	2023	Yavatmal	74.4	7.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-044	Krishna Thakre	SAMPLE-2023-CSE-044	Computer Science and Engineering (CSE)	Final Year	SC	Male	2003-04-13	0000000000 (dummy)	student044.cse4@example.com	2023	Buldhana	95.3	7.15	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-045	Tanmay Kamble	SAMPLE-2023-CSE-045	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Male	2003-09-14	0000000000 (dummy)	student045.cse4@example.com	2023	Akola	71.8	9.21	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-046	Saanvi Dange	SAMPLE-2023-CSE-046	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Female	2003-09-04	0000000000 (dummy)	student046.cse4@example.com	2023	Jalgaon	95.1	9.12	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-047	Pooja Gawande	SAMPLE-2023-CSE-047	Computer Science and Engineering (CSE)	Final Year	OBC	Female	2003-08-28	0000000000 (dummy)	student047.cse4@example.com	2023	Akola	90.7	6.52	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-048	Vaishnavi Dawande	SAMPLE-2023-CSE-048	Computer Science and Engineering (CSE)	Final Year	NT-C	Female	2003-12-13	0000000000 (dummy)	student048.cse4@example.com	2023	Buldhana	75.9	9.06	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-049	Rahul Shaikh	SAMPLE-2023-CSE-049	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Male	2003-01-08	0000000000 (dummy)	student049.cse4@example.com	2023	Buldhana	66.7	7.16	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-050	Simran Pund	SAMPLE-2023-CSE-050	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Female	2003-12-11	0000000000 (dummy)	student050.cse4@example.com	2023	Washim	76.5	8.37	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-051	Janvi Nimje	SAMPLE-2023-CSE-051	Computer Science and Engineering (CSE)	Final Year	OBC	Female	2003-07-10	0000000000 (dummy)	student051.cse4@example.com	2023	Aurangabad	70.9	5.61	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-052	Sai Khan	SAMPLE-2023-CSE-052	Computer Science and Engineering (CSE)	Final Year	NT-B	Male	2003-10-15	0000000000 (dummy)	student052.cse4@example.com	2023	Washim	70.4	5.78	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-053	Om Chavan	SAMPLE-2023-CSE-053	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Male	2003-08-26	0000000000 (dummy)	student053.cse4@example.com	2023	Aurangabad	77.5	6.13	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-054	Nikhil Bhoyar	SAMPLE-2023-CSE-054	Computer Science and Engineering (CSE)	Final Year	VJ/DT	Male	2003-01-20	0000000000 (dummy)	student054.cse4@example.com	2023	Chandrapur	66.4	6.56	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-055	Myra Rathod	SAMPLE-2023-CSE-055	Computer Science and Engineering (CSE)	Final Year	SC	Female	2003-10-03	0000000000 (dummy)	student055.cse4@example.com	2023	Nashik	79.2	8.52	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-056	Priya Kadam	SAMPLE-2023-CSE-056	Computer Science and Engineering (CSE)	Final Year	SBC	Female	2003-12-23	0000000000 (dummy)	student056.cse4@example.com	2023	Nashik	84.3	8.77	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-057	Nandini Dhole	SAMPLE-2023-CSE-057	Computer Science and Engineering (CSE)	Final Year	OBC	Female	2003-08-01	0000000000 (dummy)	student057.cse4@example.com	2023	Chandrapur	85.4	9.73	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-058	Parth Tiwari	SAMPLE-2023-CSE-058	Computer Science and Engineering (CSE)	Final Year	OPEN	Male	2003-05-24	0000000000 (dummy)	student058.cse4@example.com	2023	Jalgaon	76.1	7.5	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-059	Shreya More	SAMPLE-2023-CSE-059	Computer Science and Engineering (CSE)	Final Year	NT-B	Female	2003-05-01	0000000000 (dummy)	student059.cse4@example.com	2023	Nagpur	99.3	7.15	FICTIONAL SAMPLE — NOT OFFICIAL
STU-CSE4-060	Aarav Mahajan	SAMPLE-2023-CSE-060	Computer Science and Engineering (CSE)	Final Year	NT-B	Male	2003-11-27	0000000000 (dummy)	student060.cse4@example.com	2023	Amravati	77.1	6.35	FICTIONAL SAMPLE — NOT OFFICIAL
"""

YEAR_MAP = {
    "First Year": (1, 1),    # (academic year, semester)
    "Second Year": (2, 3),
    "Third Year": (3, 5),
    "Final Year": (4, 7),
}


class Command(BaseCommand):
    help = "Imports 240 custom CSE students into EduManager"

    def handle(self, *args, **options):
        self.stdout.write("Starting import of 240 CSE students...")

        # Get or create CSE department & B.Tech CSE Course
        dept, _ = Department.objects.get_or_create(
            code="CSE",
            defaults={
                "name": "Computer Science and Engineering",
                "description": "Department of Computer Science and Engineering"
            }
        )

        course, _ = Course.objects.get_or_create(
            code="BT-CSE",
            defaults={
                "name": "B.Tech Computer Science & Engineering",
                "department": dept,
                "duration": 4,
                "status": "active"
            }
        )

        lines = [line.strip() for line in RAW_STUDENTS_DATA.strip().split("\n") if line.strip()]
        imported_count = 0
        updated_count = 0

        with transaction.atomic():
            for idx, line in enumerate(lines, start=1):
                parts = [p.strip() for p in line.split("\t")]
                if len(parts) < 12:
                    continue

                student_id = parts[0]
                full_name = parts[1]
                enrollment_no = parts[2]
                branch_name = parts[3]
                year_str = parts[4]
                category = parts[5]
                gender_str = parts[6].lower()
                dob_str = parts[7]
                mobile_raw = parts[8]
                email_val = parts[9].lower()
                adm_year_val = parts[10]
                city_val = parts[11]

                # Name parsing
                name_tokens = full_name.split(" ", 1)
                first_name = name_tokens[0]
                last_name = name_tokens[1] if len(name_tokens) > 1 else ""

                # Year and semester
                acad_year, semester = YEAR_MAP.get(year_str, (1, 1))

                # DOB
                try:
                    dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                except Exception:
                    dob = date(2004, 1, 1)

                # Admission Date
                try:
                    adm_year = int(adm_year_val)
                    adm_date = date(adm_year, 8, 1)
                except Exception:
                    adm_date = date(2026, 8, 1)

                # Clean phone number
                phone_clean = f"98{str(idx).zfill(8)}"

                # Gender
                gender = "male" if gender_str == "male" else ("female" if gender_str == "female" else "other")

                # Unique username based on student_id: STU-CSE1-001 -> stu_cse1_001
                username = student_id.lower().replace("-", "_")

                # Create or update user
                user, u_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email_val,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": "student",
                        "phone": phone_clean,
                        "is_active": True,
                    }
                )
                if u_created:
                    user.set_password("StudentPass123!")
                    user.save()

                # Create or update Student record
                student, s_created = Student.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        "user": user,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email_val,
                        "phone": phone_clean,
                        "date_of_birth": dob,
                        "gender": gender,
                        "address": f"Address in {city_val}, Maharashtra",
                        "city": city_val,
                        "state": "Maharashtra",
                        "pincode": "444601",
                        "department": dept,
                        "course": course,
                        "year": acad_year,
                        "semester": semester,
                        "admission_date": adm_date,
                        "status": "active",
                    }
                )

                if s_created:
                    imported_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed {len(lines)} records! (Imported: {imported_count}, Updated: {updated_count})"
        ))
        self.stdout.write(self.style.SUCCESS(f"Total students in database: {Student.objects.count()}"))
