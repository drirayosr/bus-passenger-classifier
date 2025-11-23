"""
Setup Pre-commit Hooks
Installs and configures pre-commit hooks for code quality
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command and print status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(e.stderr)
        return False

def main():
    print("\n🚀 Setting up Pre-commit Hooks")
    print("="*60)
    
    # Install pre-commit
    print("\n1. Installing pre-commit...")
    if not run_command("pip install pre-commit", "Installing pre-commit"):
        sys.exit(1)
    
    # Install the git hooks
    print("\n2. Installing git hooks...")
    if not run_command("pre-commit install", "Installing git hooks"):
        sys.exit(1)
    
    # Install commit-msg hook
    print("\n3. Installing commit-msg hook...")
    run_command("pre-commit install --hook-type commit-msg", "Installing commit-msg hook")
    
    # Run hooks on all files (optional but recommended)
    print("\n4. Running hooks on all existing files (this may take a minute)...")
    print("⚠️  This will auto-format your code. Continue? (y/n): ", end="")
    
    # Auto-continue for automation
    choice = input().lower() if sys.stdin.isatty() else 'y'
    
    if choice == 'y':
        run_command("pre-commit run --all-files", "Running all hooks")
    
    print("\n" + "="*60)
    print("✅ Pre-commit hooks setup complete!")
    print("="*60)
    print("\n📝 What happens now:")
    print("   • Every commit will automatically:")
    print("     - Format code with black")
    print("     - Sort imports with isort")
    print("     - Lint with flake8")
    print("     - Check for security issues")
    print("     - Remove trailing whitespace")
    print("     - Validate YAML/JSON files")
    print("\n💡 To run hooks manually:")
    print("   pre-commit run --all-files")
    print("\n💡 To skip hooks (not recommended):")
    print("   git commit --no-verify -m 'message'")
    print("\n🎉 Your code quality is now automated!")

if __name__ == "__main__":
    main()
