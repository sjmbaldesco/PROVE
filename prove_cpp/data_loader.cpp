#include "data_loader.h"
#include <fstream>
#include <iostream>
#include <algorithm>
#include <cstdlib>

namespace data_loader {

std::unordered_set<std::string> blocklist_set;
std::unordered_set<std::string> ugc_platforms_set;

std::string normalize_domain(const std::string& netloc) {
    std::string host = netloc;
    std::transform(host.begin(), host.end(), host.begin(), ::tolower);
    host.erase(0, host.find_first_not_of(" \t\r\n"));
    host.erase(host.find_last_not_of(" \t\r\n") + 1);
    
    if (host.length() >= 4 && host.substr(0, 4) == "www.") host = host.substr(4);
    auto at_pos = host.rfind("@");
    if (at_pos != std::string::npos) host = host.substr(at_pos + 1);
    auto colon_pos = host.find(":");
    if (colon_pos != std::string::npos) host = host.substr(0, colon_pos);
    return host;
}

std::unordered_set<std::string> read_csv_domains(const std::string& path) {
    std::unordered_set<std::string> out;
    std::ifstream f(path);
    if (!f.is_open()) {
        std::cerr << "Warning: Missing dataset or could not read: " << path << "\n";
        return out;
    }
    std::string line;
    while (std::getline(f, line)) {
        std::string domain = normalize_domain(line);
        if (!domain.empty()) {
            auto comma = domain.find(',');
            if (comma != std::string::npos) domain = domain.substr(0, comma);
            if (!domain.empty()) out.insert(domain);
        }
    }
    return out;
}

void load_datasets() {
    std::string data_dir = "data";
    blocklist_set = read_csv_domains(data_dir + "/blocklist.csv");
    ugc_platforms_set = read_csv_domains(data_dir + "/ugc_platforms.csv");
}

void append_to_blocklist(const std::string& domain) {
    std::string data_dir = "data";
    std::system("mkdir data 2> NUL");
    std::string normalized = normalize_domain(domain);
    if (normalized.empty()) throw std::invalid_argument("Empty domain");
    
    std::ofstream f(data_dir + "/blocklist.csv", std::ios::app);
    if (f.is_open()) {
        f << normalized << "\n";
    }
}

} // namespace
