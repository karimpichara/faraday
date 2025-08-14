#!/bin/bash

# Database Seeding Helper Script for Faraday Project
# This script provides an easy way to validate and seed the database

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🌱 Faraday Database Seeding Helper${NC}"
echo "=================================="
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  test     - Run validation tests to check if environment is ready"
    echo "  seed     - Run the database seeding (will run tests first)"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test    # Check if environment is ready for seeding"
    echo "  $0 seed    # Validate and then seed the database"
    echo ""
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}🧪 Running environment validation...${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    python scripts/test_seed.py
    
    return $?
}

# Function to run seeding
run_seeding() {
    echo -e "${YELLOW}🌱 Starting database seeding...${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    python scripts/seed_database.py
    
    return $?
}

# Main logic
case "${1:-}" in
    "test")
        echo -e "${BLUE}Running validation tests only...${NC}"
        echo ""
        if run_tests; then
            echo ""
            echo -e "${GREEN}✅ Validation completed successfully!${NC}"
            echo -e "${GREEN}   Environment is ready for seeding.${NC}"
            echo ""
            echo "To run the actual seeding:"
            echo "  $0 seed"
        else
            echo ""
            echo -e "${RED}❌ Validation failed!${NC}"
            echo -e "${RED}   Please fix the issues before running seeding.${NC}"
            exit 1
        fi
        ;;
    "seed")
        echo -e "${BLUE}Running validation and seeding...${NC}"
        echo ""
        
        # First run tests
        if run_tests; then
            echo ""
            echo -e "${GREEN}✅ Validation passed! Proceeding with seeding...${NC}"
            echo ""
            
            # Ask for confirmation
            read -p "Do you want to proceed with database seeding? (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if run_seeding; then
                    echo ""
                    echo -e "${GREEN}🎉 Database seeding completed successfully!${NC}"
                    echo ""
                    echo "You can now test your application with the populated data."
                    echo ""
                    echo "Sample user credentials:"
                    echo "  • supervisor_sen / password123"
                    echo "  • supervisor_ics / password123" 
                    echo "  • supervisor_tds / password123"
                else
                    echo ""
                    echo -e "${RED}❌ Seeding failed!${NC}"
                    exit 1
                fi
            else
                echo ""
                echo -e "${YELLOW}⏸ Seeding cancelled by user.${NC}"
            fi
        else
            echo ""
            echo -e "${RED}❌ Validation failed! Cannot proceed with seeding.${NC}"
            echo -e "${RED}   Please fix the validation errors first.${NC}"
            exit 1
        fi
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    "")
        echo -e "${YELLOW}No command specified.${NC}"
        echo ""
        show_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
