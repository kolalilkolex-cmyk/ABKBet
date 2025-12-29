#!/bin/bash
# Quick Commands for PythonAnywhere Fresh Deployment

echo "=========================================="
echo "ABKBet PythonAnywhere - Quick Setup"
echo "=========================================="

# Function to print colored output
print_step() {
    echo ""
    echo ">>> $1"
    echo ""
}

print_success() {
    echo "✓ $1"
}

print_error() {
    echo "✗ $1"
}

# STEP 1: Backup and Clean
backup_and_clean() {
    print_step "STEP 1: Backup and Clean"
    
    cd /home/Lilkolex
    
    # Backup database if exists
    if [ -f "betting.db" ]; then
        cp betting.db "betting_backup_$(date +%Y%m%d_%H%M%S).db"
        print_success "Database backed up"
    fi
    
    if [ -f "instance/betting.db" ]; then
        cp instance/betting.db "betting_backup_$(date +%Y%m%d_%H%M%S).db"
        print_success "Database backed up"
    fi
    
    # Remove old directories
    rm -rf ABKBet ABKBet_old pythonanywhere_* 2>/dev/null
    print_success "Old files removed"
}

# STEP 2: Extract Files
extract_files() {
    print_step "STEP 2: Extract Files"
    
    cd /home/Lilkolex
    
    # Find the zip file
    ZIP_FILE=$(ls -t ABKBet_Complete_Fixed_*.zip 2>/dev/null | head -1)
    
    if [ -z "$ZIP_FILE" ]; then
        print_error "No deployment package found. Upload ABKBet_Complete_Fixed_*.zip first!"
        return 1
    fi
    
    print_success "Found: $ZIP_FILE"
    
    # Extract
    mkdir -p ABKBet
    unzip -q "$ZIP_FILE" -d ABKBet
    print_success "Files extracted to /home/Lilkolex/ABKBet"
    
    # Verify
    cd ABKBet
    if [ -f "run.py" ] && [ -d "app" ]; then
        print_success "Extraction verified"
    else
        print_error "Extraction failed - files missing"
        return 1
    fi
}

# STEP 3: Setup Virtual Environment
setup_venv() {
    print_step "STEP 3: Setup Virtual Environment"
    
    # Create venv if it doesn't exist
    if [ ! -d "/home/Lilkolex/.virtualenvs/abkbet_env" ]; then
        mkvirtualenv --python=/usr/bin/python3.10 abkbet_env
        print_success "Virtual environment created"
    else
        workon abkbet_env
        print_success "Virtual environment activated"
    fi
    
    # Install requirements
    cd /home/Lilkolex/ABKBet
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    print_success "Requirements installed"
    
    # Verify key packages
    pip list | grep -i "Flask\|SQLAlchemy\|JWT" | head -5
}

# STEP 4: Setup Database
setup_database() {
    print_step "STEP 4: Setup Database"
    
    cd /home/Lilkolex/ABKBet
    workon abkbet_env
    
    # Create instance directory
    mkdir -p instance
    chmod 755 instance
    print_success "Instance directory created"
    
    # Check if backup exists to restore
    BACKUP_DB=$(ls -t /home/Lilkolex/betting_backup_*.db 2>/dev/null | head -1)
    
    if [ -n "$BACKUP_DB" ]; then
        cp "$BACKUP_DB" instance/betting.db
        chmod 664 instance/betting.db
        print_success "Database restored from backup: $(basename $BACKUP_DB)"
    else
        # Create fresh database
        python << 'EOF'
from app import create_app, db
from app.models import User
from app.utils.auth import hash_password

app = create_app('production')
with app.app_context():
    db.create_all()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@abkbet.com',
        password_hash=hash_password('admin123'),
        balance=1000.0,
        is_admin=True,
        is_active=True
    )
    db.session.add(admin)
    
    # Create test user
    test = User(
        username='testuser',
        email='test@abkbet.com',
        password_hash=hash_password('test123'),
        balance=100.0,
        is_active=True
    )
    db.session.add(test)
    
    db.session.commit()
    print('✓ Fresh database created with admin and test users')
EOF
        print_success "Fresh database created"
        echo "  Admin: admin / admin123"
        echo "  Test: testuser / test123"
    fi
    
    # Verify database
    python << 'EOF'
from app import create_app, db
from app.models import User, Match, Bet
from sqlalchemy import inspect

app = create_app('production')
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'Tables: {len(tables)} ({", ".join(sorted(tables)[:5])}...)')
    print(f'Users: {User.query.count()}')
    print(f'Matches: {Match.query.count()}')
    print(f'Bets: {Bet.query.count()}')
EOF
}

# STEP 5: Verify Deployment
verify_deployment() {
    print_step "STEP 5: Verify Deployment"
    
    cd /home/Lilkolex/ABKBet
    workon abkbet_env
    
    # Test import
    python -c "from run import flask_app; print('✓ App imports successfully')" || {
        print_error "App import failed"
        return 1
    }
    
    # Test database
    python -c "from app import create_app, db; from app.models import User; app=create_app('production'); app.app_context().push(); print(f'✓ Database accessible ({User.query.count()} users)')" || {
        print_error "Database access failed"
        return 1
    }
    
    # Test routes
    python << 'EOF'
from run import flask_app
routes = [str(r) for r in flask_app.url_map.iter_rules()]
critical = ['/api/health', '/api/auth/login', '/api/bets/matches/manual']
print(f'✓ {len(routes)} routes registered')
for r in critical:
    if any(r in route for route in routes):
        print(f'  ✓ {r}')
EOF
    
    print_success "All checks passed!"
}

# Main execution
main() {
    echo ""
    read -p "This will delete all old files and deploy fresh. Continue? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    
    backup_and_clean || exit 1
    extract_files || exit 1
    setup_venv || exit 1
    setup_database || exit 1
    verify_deployment || exit 1
    
    echo ""
    echo "=========================================="
    echo "DEPLOYMENT COMPLETE!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Go to PythonAnywhere Web tab"
    echo "2. Configure WSGI file (see FRESH_DEPLOYMENT_GUIDE.md Step 6.2)"
    echo "3. Set virtual environment to: /home/Lilkolex/.virtualenvs/abkbet_env"
    echo "4. Set static files: URL=/static/ Path=/home/Lilkolex/ABKBet/static/"
    echo "5. Click Reload button"
    echo "6. Test: https://lilkolex.pythonanywhere.com"
    echo ""
}

# Run main function
main
