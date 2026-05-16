# Product Requirements Document (PRD)

# Project Name

GetExpertCompta

---

# Project Type

Pan-African Web Platform for Connecting Businesses and Certified Accountants

---

# Vision

GetExpertCompta is a professional digital platform designed to connect companies and accounting experts across Africa.

The platform helps:

- Businesses quickly find trusted accountants
- Experts gain visibility and business opportunities
- Clients verify expert availability in real-time
- Companies subscribe to premium access for more expert visibility

The platform must prioritize:

- trust
- professionalism
- security
- scalability
- African payment integration
- multi-country support

---

# Business Objective

The business model is based on a Freemium + Premium Subscription system.

## Free Access

Visitors can:
- view up to 3 accounting experts
- explore limited profiles
- understand platform value

Goal:
Convert visitors into premium subscribers.

---

## Premium Access

Premium companies can:
- access unlimited experts
- use advanced filters
- send more service requests
- access priority support
- access verified experts

Subscription plans:
- Weekly
- Monthly
- Quarterly
- Yearly

---

# Target Market

Primary Market:
- Cameroon
- Mali
- French-speaking African countries

Future Expansion:
- Entire Africa

---

# Main Users

## 1. Business / Company

Capabilities:
- register/login
- search accountants
- filter experts
- send accounting requests
- subscribe to premium plans
- leave reviews
- manage requests history

---

## 2. Accounting Expert

Capabilities:
- create professional profile
- upload credentials/documents
- define specialties
- manage availability status
- receive requests
- respond to opportunities

Availability statuses:
- Available
- Unavailable

Quick actions:
- "I am available"
- "I am not available"

---

## 3. Administrator

Capabilities:
- validate experts
- manage users
- moderate reviews
- monitor payments
- manage subscriptions
- monitor reports
- manage support
- view analytics

---

# Core Features

# Public Website

Pages:
- Home
- How It Works
- Pricing
- FAQ
- Contact
- Login/Register

Homepage must:
- present platform value proposition
- display only 3 experts in free mode
- encourage premium upgrade

---

# Authentication System

Requirements:
- secure registration/login
- JWT or session authentication
- role-based permissions
- email verification
- password reset
- secure password hashing

Roles:
- Admin
- Business
- Expert

Recommended:
- Django Allauth
- JWT authentication
- RBAC permissions

---

# Expert Profile System

Each expert profile must include:
- profile picture
- full name
- professional title
- country
- city
- specialties
- years of experience
- certifications
- availability status
- profile verification badge
- ratings/reviews

Optional:
- CV upload
- portfolio
- LinkedIn profile

---

# Expert Availability System

Experts can manually toggle status:
- Available
- Unavailable

Businesses must clearly see expert availability before sending requests.

Optional future improvement:
- auto-expiration after inactivity

---

# Business Request System

Businesses can:
- submit accounting requests
- specify country
- specify accounting needs
- attach files
- select experts

Experts can:
- accept request
- decline request
- indicate availability

---

# Review & Rating System

Businesses can leave:
- ratings
- reviews
- feedback

Requirements:
- only verified interactions can review
- anti-spam moderation
- admin moderation tools

---

# Subscription System

Subscription plans:
- Weekly
- Monthly
- Quarterly
- Yearly

Requirements:
- subscription activation
- expiration tracking
- upgrade/downgrade
- premium restrictions
- invoices/history

Recommended:
- modular payment architecture

---

# African Payment Integration

Supported payments:
- Orange Money
- Wave
- Malitel Money

Future-ready architecture required.

Recommended:
- payment abstraction layer
- provider adapters

Requirements:
- payment logs
- webhook validation
- transaction history
- retry mechanisms

---

# Admin Dashboard

Admin dashboard must include:
- user management
- expert verification
- payment tracking
- subscription management
- analytics
- reports
- moderation tools
- support tickets

---

# Security Requirements

This project handles sensitive business data.

Cursor MUST follow enterprise-grade security best practices.

Mandatory security requirements:

## Authentication & Authorization
- RBAC permissions
- secure session handling
- CSRF protection
- XSS protection
- SQL injection prevention
- rate limiting
- brute-force protection

---

## Data Security
- hashed passwords
- encrypted sensitive data
- secure file uploads
- audit logging
- automatic backups

---

## Infrastructure Security
- HTTPS only
- secure environment variables
- production-ready settings
- Docker support
- separated dev/staging/prod configs

---

## Compliance
- privacy policy ready
- terms of service ready
- consent handling
- GDPR-inspired architecture

---

# Technical Stack

Backend:
- Python 3.12+
- Django 5+
- Django REST Framework

Frontend:
- Django Templates OR React frontend (Cursor may choose best approach)

Database:
- PostgreSQL

Authentication:
- Django Allauth
- JWT Authentication

Task Queue:
- Celery + Redis

File Storage:
- AWS S3 compatible storage OR local development storage

Deployment:
- Docker
- Docker Compose
- Nginx
- Gunicorn

Caching:
- Redis

Environment:
- Python virtual environment (venv)

IMPORTANT:
The project MUST be developed inside a Python virtual environment.

---

# Development Environment

Project name:
GetExpertCompta

Setup requirements:
- use venv
- use .env variables
- modular architecture
- scalable architecture
- production-ready structure

---

# Recommended Django Apps Structure

GetExpertCompta/
│
├── accounts/
├── experts/
├── businesses/
├── subscriptions/
├── payments/
├── reviews/
├── requests_system/
├── notifications/
├── dashboard/
├── core/
├── api/
└── adminpanel/

---

# API Requirements

REST API required.

Recommended:
- Django REST Framework
- OpenAPI / Swagger documentation

API must support:
- authentication
- expert search
- subscription management
- payment processing
- review management

---

# Search & Filtering

Businesses must be able to filter experts by:
- country
- city
- specialty
- availability
- ratings
- years of experience

Recommended:
- PostgreSQL full-text search

---

# Notifications System

Required notifications:
- request received
- request accepted
- subscription expiration
- payment confirmation

Future-ready:
- email notifications
- SMS notifications
- WhatsApp notifications

---

# KYC & Verification System

Experts must upload:
- identity documents
- certifications
- professional proof

Admin validates manually.

Statuses:
- Pending
- Verified
- Rejected

Verified experts receive:
- verification badge

---

# Scalability Requirements

Architecture must support:
- multi-country expansion
- high traffic
- modular growth
- future mobile applications

Code must be:
- clean
- maintainable
- scalable
- documented

---

# UX/UI Guidelines

The platform should feel:
- modern
- trustworthy
- professional
- enterprise-grade

Design style:
- minimalist
- clean dashboard
- responsive
- mobile-first

---

# Recommended Additional Technologies

Cursor may use:
- Tailwind CSS
- HTMX
- Alpine.js
- React (if necessary)
- DRF Spectacular
- Celery
- Redis
- Docker

ONLY if they improve:
- maintainability
- scalability
- security
- developer experience

---

# DevOps Requirements

Cursor must configure:
- .env.example
- requirements.txt
- Docker support
- logging system
- health checks
- backup strategy

---

# Git & Code Standards

Requirements:
- modular commits
- clean architecture
- SOLID principles
- reusable services
- repository pattern where useful

Code quality:
- typed where possible
- documented
- linted

Recommended:
- black
- flake8
- pre-commit hooks

---

# MVP Scope (Version 1)

The first release MUST include:

## Public Site
- homepage
- pricing
- login/register
- limited experts preview

## Expert Space
- profile management
- availability toggle
- requests management

## Business Space
- expert browsing
- premium subscription
- request sending
- reviews

## Admin
- expert verification
- payment management
- user management

---

# Out of Scope for V1

DO NOT implement initially:
- AI matching
- video calls
- native mobile app
- advanced analytics
- real-time chat
- blockchain
- complex recommendation engine

Focus on:
- stability
- clean architecture
- security
- scalability

---

# Deliverables

Cursor must generate:

- complete Django project
- modular architecture
- REST API
- authentication system
- database models
- Docker configuration
- venv setup instructions
- secure settings
- production-ready structure
- responsive UI
- admin dashboard
- documentation

---

# Final Instructions For Cursor

Execute the project step-by-step.

Do not skip architecture decisions.

Prioritize:
- security
- scalability
- maintainability
- clean code

Use industry best practices for:
- Software Engineering
- Information Systems Security
- Backend Architecture
- Authentication
- Payments
- DevOps

The project must be enterprise-grade and production-ready.

Generate all files required for a professional SaaS platform.