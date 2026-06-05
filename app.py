import sys
import os
import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core_backend.storage import LocalStorageEngine
from core_backend.engine import HousingEngine

class KejaScoutMobile(toga.App):
    def startup(self):
        self.storage_manager = LocalStorageEngine("../storage")
        self.engine = HousingEngine(self.storage_manager)
        self.acting_user = "demo_student"

        self.app_container = toga.Box(style=Pack(direction=COLUMN, background_color="#0A1F44"))
        self.main_window = toga.MainWindow(title="KejaScout App Engine", content=self.app_container)
        self.main_window.show()

        self.trigger_brand_splash()

    def trigger_brand_splash(self):
        splash_box = toga.Box(style=Pack(direction=COLUMN, alignment="center", padding_top=100))
        
        splash_box.add(toga.Label("Housing App", style=Pack(font_size=32, text_align="center")))
        splash_box.add(toga.Label("KejaScout", style=Pack(font_size=26, font_weight="bold", color="#00A86B", margin_top=12)))
        splash_box.add(toga.Label("Smart. Verified. Safe.", style=Pack(font_size=12, color="#F8F9FA", font_style="italic")))
        
        self.app_container.add(splash_box)
        self.add_background_task(lambda app: self.wait_and_fade(2))

    def wait_and_fade(self, delay_duration):
        import time
        time.sleep(delay_duration)
        self.display_gateway_screen()

    def display_gateway_screen(self):
        self.app_container.clear()
        self.app_container.style.background_color = "#F8F9FA"

        gateway = toga.Box(style=Pack(direction=COLUMN, padding=24))
        gateway.add(toga.Label("Welcome to KejaScout", style=Pack(font_size=20, font_weight="bold", color="#0A1F44")))
        gateway.add(toga.Label("Authenticate securely to unlock verified local student bases.", style=Pack(font_size=11, color="#666666", margin_bottom=40)))

        google_auth = toga.Button(
            "Continue with Google Account", 
            on_press=self.display_split_road, 
            style=Pack(margin_bottom=12, background_color="#FFFFFF")
        )
        mobile_auth = toga.Button(
            "Register using Safaricom / Airtel Number", 
            on_press=self.display_split_road, 
            style=Pack(background_color="#0A1F44", color="#FFFFFF")
        )

        gateway.add(google_auth)
        gateway.add(mobile_auth)
        self.app_container.add(gateway)

    def display_split_road(self, widget):
        self.app_container.clear()
        split = toga.Box(style=Pack(direction=COLUMN, padding=24))
        split.add(toga.Label("State Your Platform Mandate:", style=Pack(font_size=16, font_weight="bold", color="#0A1F44", margin_bottom=25)))

        tenant_card = toga.Button(
            "I am a Student / Tenant\n(Search rooms and review campus safety parameters)",
            on_press=self.initiate_student_feed,
            style=Pack(padding=16, margin_bottom=16, background_color="#FFFFFF")
        )
        landlord_card = toga.Button(
            "I am a Property Owner / Landlord\n(Submit National ID to request verification status)",
            on_press=self.initiate_landlord_hold,
            style=Pack(padding=16, background_color="#FFFFFF")
        )

        split.add(tenant_card)
        split.add(landlord_card)
        self.app_container.add(split)

    def initiate_student_feed(self, widget):
        self.acting_user = "demo_student"
        self.engine.register_user(self.acting_user, "student")
        self.main_window.info_dialog("KejaScout Security Status", "Tenant Environment unlocked. AI analysis modules standing by.")
        self.build_discovery_viewport()

    def initiate_landlord_hold(self, widget):
        self.acting_user = "demo_landlord"
        self.engine.register_user(self.acting_user, "landlord")
        
        self.app_container.clear()
        hold_box = toga.Box(style=Pack(direction=COLUMN, padding=24, alignment="center"))
        hold_box.add(toga.Label("Verification Shield Active", style=Pack(font_size=16, font_weight="bold", color="#F5A623")))
        hold_box.add(toga.Label("To block platform scammers, you are restricted from posting listings until your physical ID card matches verified land records.", style=Pack(margin_bottom=25, font_size=11, text_align="center")))
        
        upload_btn = toga.Button(
            "Take Photo of National ID Card", 
            on_press=self.execute_mock_landlord_verification, 
            style=Pack(background_color="#0A1F44", color="#FFFFFF")
        )
        hold_box.add(upload_btn)
        self.app_container.add(hold_box)

    def execute_mock_landlord_verification(self, widget):
        self.engine.submit_verification_id(self.acting_user, "national_id_card.png")
        self.main_window.info_dialog("Audit Matrix updated", "National ID records captured cleanly. Profile shifted to 'Admin Evaluation Status'. Approval SMS will ping shortly.")
        self.display_gateway_screen()

    def build_discovery_viewport(self):
        self.app_container.clear()
        scroll_wrapper = toga.Box(style=Pack(direction=COLUMN, padding=16))
        
        scroll_wrapper.add(toga.Label("KejaScout Live Feed", style=Pack(font_size=18, font_weight="bold", color="#0A1F44")))
        
        self.search_field = toga.TextInput(placeholder="Enter University target (e.g. JKUAT)", style=Pack(margin_top=8, margin_bottom=8))
        search_btn = toga.Button("Execute Target Match", on_press=self.filter_listings, style=Pack(background_color="#0A1F44", color="#FFFFFF"))
        
        scroll_wrapper.add(self.search_field)
        scroll_wrapper.add(search_btn)

        self.cards_viewport = toga.Box(style=Pack(direction=COLUMN, margin_top=15))
        scroll_wrapper.add(self.cards_viewport)
        self.app_container.add(scroll_wrapper)

        self.populate_cards(self.engine.get_all_properties())

    def populate_cards(self, listings_source):
        self.cards_viewport.clear()
        for item in listings_source:
            card = toga.Box(style=Pack(direction=COLUMN, padding=12, background_color="#FFFFFF", margin_bottom=12))
            
            lbl_title = toga.Label(f"{item['type']} — Near {item['nearest_landmark']}", style=Pack(font_weight="bold", color="#0A1F44"))
            lbl_pricing = toga.Label(f"Rent: KSh {item['price']:,} / Month [Verified Contract: {item['is_verified']}]", style=Pack(font_size=10, color="#666666"))
            
            card.add(lbl_title)
            card.add(lbl_pricing)

            actions = toga.Box(style=Pack(direction=ROW, margin_top=8))
            book_action = toga.Button(
                "M-Pesa 10% Lock", 
                on_press=lambda w, p=item['property_id']: self.trigger_safelock_escrow(p),
                style=Pack(background_color="#00A86B", color="#FFFFFF", margin_right=6)
            )
            report_action = toga.Button(
                "Flag Fraud", 
                on_press=lambda w, p=item['property_id']: self.trigger_fraud_flag(p),
                style=Pack(background_color="#F5A623", color="#FFFFFF")
            )
            
            actions.add(book_action)
            actions.add(report_action)
            card.add(actions)
            
            self.cards_viewport.add(card)

    def filter_listings(self, widget):
        target = self.search_field.value.strip()
        if target:
            matched = self.engine.search_and_filter(university=target)
            self.populate_cards(matched)
        else:
            self.populate_cards(self.engine.get_all_properties())

    def trigger_safelock_escrow(self, property_id):
        success, feedback = self.engine.process_safelock_trigger(property_id, self.acting_user)
        if success:
            self.main_window.info_dialog("Safaricom Daraja STK Push Active", f"{feedback}\n\nLandlord alert triggered. Unlocking 2-Hour connection.")
        else:
            self.main_window.error_dialog("Escrow Blocked", feedback)

    def trigger_fraud_flag(self, property_id):
        success, feedback = self.engine.report_listing(property_id)
        self.main_window.info_dialog("Safety Ledger Module", feedback)
        self.populate_cards(self.engine.get_all_properties())

def main():
    return KejaScoutMobile("KejaScout Core Engine", "org.kejascout.kenya")
