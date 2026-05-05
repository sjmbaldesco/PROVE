#pragma once
#include <string>
#include <tuple>
#include <unordered_set>

std::tuple<std::string, std::string> process_input(const std::string& raw);
std::string evaluate_credibility(const std::string& input_type, const std::string& parsed_value);
