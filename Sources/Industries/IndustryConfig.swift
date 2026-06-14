import Foundation

/// Canonical identifier for each industry shipped inside JB Glossary.
///
/// Adding industry #5+: append a case here, create a `Sources/Industries/<Industry>Brand.swift`,
/// register it in `IndustryConfig.all`, and add a `glossary_<industry>.json` to the bundle.
enum IndustryID: String, CaseIterable, Identifiable, Codable {
    case pharma
    case ai
    case law
    case finance
    case realEstate
    case insurance
    case robotics

    var id: String { rawValue }
}

/// Pairs an industry's brand identity with its StoreKit product. Every
/// industry has an IAP — letters A–D (`IndustryConfig.freeLetters`) are free
/// as a taster, E–Z is gated by this IAP.
struct IndustryConfig: Identifiable {
    let id: IndustryID
    let brand: Brand
    /// StoreKit product identifier the user purchases to unlock letters E–Z
    /// for this industry.
    let iapProductID: String
}

extension IndustryConfig {
    /// Letters that are free in every industry as a taster — substantial
    /// enough (~25–29% of each industry's terms) to demonstrate value, small
    /// enough to leave a real reason to buy.
    static let freeLetters: Set<String> = ["A", "B", "C", "D"]

    /// Registry — order here is the canonical display order in the picker.
    static let all: [IndustryConfig] = [
        .init(id: .pharma,     brand: pharmaBrand,     iapProductID: "com.jamesbrowne.JBGlossary.pharma"),
        .init(id: .ai,         brand: aiBrand,         iapProductID: "com.jamesbrowne.JBGlossary.ai"),
        .init(id: .law,        brand: lawBrand,        iapProductID: "com.jamesbrowne.JBGlossary.law"),
        .init(id: .finance,    brand: financeBrand,    iapProductID: "com.jamesbrowne.JBGlossary.finance"),
        .init(id: .realEstate, brand: realEstateBrand, iapProductID: "com.jamesbrowne.JBGlossary.realEstate"),
        .init(id: .insurance,  brand: insuranceBrand,  iapProductID: "com.jamesbrowne.JBGlossary.insurance"),
        .init(id: .robotics,   brand: roboticsBrand,   iapProductID: "com.jamesbrowne.JBGlossary.robotics"),
    ]

    /// Look up an industry by ID. Safe to force-unwrap because `IndustryID`
    /// cases are 1:1 with `all` entries; a missing case is a programmer error.
    static func config(for id: IndustryID) -> IndustryConfig {
        all.first { $0.id == id }!
    }

    /// Set the global `Brand.current` so all existing call sites (PGColors,
    /// AboutView, FilterSheet, SplashView, Hyperlinks, GlossaryStore, etc.)
    /// see the right industry's brand. Call before mounting an industry's
    /// view tree.
    static func activate(_ id: IndustryID) {
        Brand.current = config(for: id).brand
    }
}

/// StoreKit product identifier for the master "All Industries" unlock.
/// Owners get every current and future paid industry's E–Z content as a free
/// entitlement.
let masterUnlockProductID = "com.jamesbrowne.JBGlossary.all"
