#include <iostream>
#include <string>
#include "classifier.h"
#include "data_loader.h"
#include "search.h"
#include "logger.h"
#include <fstream>

void display_menu() {
    std::cout << "\n=== P.R.O.V.E. ===\n";
    std::cout << "[1] Submit URL or claim\n";
    std::cout << "[2] Flag a domain to blocklist\n";
    std::cout << "[3] View recent log entries\n";
    std::cout << "[0] Exit\n";
    std::cout << "Select an option: ";
}

int main() {
    data_loader::load_datasets();
    std::string input;
    
    while (true) {
        display_menu();
        if (!std::getline(std::cin, input)) break;
        
        if (input == "0") {
            break;
        } else if (input == "1") {
            std::cout << "Enter URL or claim: ";
            std::string query;
            if (!std::getline(std::cin, query)) break;
            
            auto res = process_input(query);
            std::string input_type = std::get<0>(res);
            std::string parsed_value = std::get<1>(res);
            std::string label = evaluate_credibility(input_type, parsed_value);
            
            std::cout << "Classification: " << label << "\n";
            
            execute_search(query);
            log_transaction(query, label);
            
            std::cout << "Browser search launched.\n";
            
        } else if (input == "2") {
            std::cout << "Enter root domain to add to the blocklist (e.g. example.com): ";
            std::string domain;
            if (!std::getline(std::cin, domain)) break;
            
            if (!domain.empty()) {
                try {
                    data_loader::append_to_blocklist(domain);
                    data_loader::load_datasets();
                    std::cout << "Added to blocklist and reloaded.\n";
                } catch (const std::exception& e) {
                    std::cout << "Error: " << e.what() << "\n";
                }
            }
        } else if (input == "3") {
            std::cout << "--- Recent Logs ---\n";
            std::ifstream f("logs/history.txt");
            if (f.is_open()) {
                std::string line;
                while (std::getline(f, line)) {
                    std::cout << line << "\n";
                }
            } else {
                std::cout << "No logs found.\n";
            }
            std::cout << "-------------------\n";
        } else {
            std::cout << "Invalid option. Try again.\n";
        }
    }
    return 0;
}
