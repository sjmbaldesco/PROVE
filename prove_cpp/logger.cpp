#include "logger.h"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <ctime>
#include <cstdlib>

std::string sanitize_for_log(const std::string& text) {
    std::string out;
    bool in_space = false;
    for (char c : text) {
        if (c == '\n' || c == '\r' || c == '\t' || c == ' ') {
            if (!in_space) {
                out += ' ';
                in_space = true;
            }
        }
        else if (c >= 32 && c <= 126) {
            out += c;
            in_space = false;
        }
    }
    if (!out.empty() && out.back() == ' ') out.pop_back();
    if (!out.empty() && out.front() == ' ') out.erase(out.begin());
    return out;
}

void log_transaction(const std::string& query, const std::string& label) {
    std::string log_dir = "logs";
    std::system("mkdir logs 2> NUL");
    
    std::time_t now = std::time(nullptr);
    std::tm* t = std::gmtime(&now);
    char buf[30];
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", t);
    
    std::ofstream f(log_dir + "/history.txt", std::ios::app);
    if (f.is_open()) {
        f << "[" << buf << "] " << sanitize_for_log(query) << " -> " << label << "\n";
    }
}
