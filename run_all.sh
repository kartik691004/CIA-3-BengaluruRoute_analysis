#!/bin/bash
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev &
wait\n