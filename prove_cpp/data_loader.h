#pragma once
#include <string>
#include <unordered_set>

namespace data_loader {
    extern std::unordered_set<std::string> blocklist_set;
    extern std::unordered_set<std::string> ugc_platforms_set;
    
    std::string normalize_domain(const std::string& netloc);
    void load_datasets();
    void append_to_blocklist(const std::string& domain);
}
