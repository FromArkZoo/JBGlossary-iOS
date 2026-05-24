import SwiftUI

enum PGFont {
    // Serif — system .serif maps to New York on iOS, the editorial direction's stand-in for Source Serif 4.
    /// "JB" stamp — Didot Italic regular weight, matching the app-icon family. Used in
    /// SplashView, EditorialHeader, PaywallSheet, IndustryPickerView. Use the explicit
    /// PostScript face name so SwiftUI always picks the real italic glyphs instead of
    /// synthesizing italic from the upright cut.
    static let jbStamp           = Font.custom("Didot-Italic", size: 28)
    static let displayItalic     = Font.custom("Didot-Italic", size: 28)
    static let termTitle         = Font.system(size: 38, weight: .bold,     design: .serif)
    static let termFullItalic    = Font.system(size: 18, weight: .regular,  design: .serif).italic()
    static let snappyItalic      = Font.system(size: 19, weight: .medium,   design: .serif).italic()
    static let body              = Font.system(size: 17, weight: .regular,  design: .serif)
    static let letterTileItalic  = Font.system(size: 20, weight: .semibold, design: .serif).italic()
    static let termRowTitle      = Font.system(size: 16, weight: .semibold, design: .serif)
    static let termRowFullItalic = Font.system(size: 13, weight: .regular,  design: .serif).italic()
    static let metaItalic        = Font.system(size: 12, weight: .regular,  design: .serif).italic()
    static let policyIcon        = Font.system(size: 17, weight: .bold,     design: .serif).italic()
    static let policyTitle       = Font.system(size: 16, weight: .semibold, design: .serif)
    static let filterTitleItalic = Font.system(size: 17, weight: .semibold, design: .serif).italic()

    // Sans — system .default (SF Pro)
    static let eyebrow           = Font.system(size: 10, weight: .bold,     design: .default)
    static let labelSmall        = Font.system(size: 9,  weight: .semibold, design: .default)
    static let chip              = Font.system(size: 13, weight: .regular,  design: .default)
    static let chipCountItalic   = Font.system(size: 11, weight: .regular,  design: .serif).italic()
    static let tileCount         = Font.system(size: 9,  weight: .medium,   design: .default)
    static let buttonLabel       = Font.system(size: 14, weight: .semibold, design: .default)
    static let applyLabel        = Font.system(size: 12, weight: .bold,     design: .default)
    static let policySub         = Font.system(size: 11, weight: .regular,  design: .default)
    static let toolbarPlain      = Font.system(size: 14, weight: .medium,   design: .default)
    static let toolbarStrong     = Font.system(size: 14, weight: .semibold, design: .default)
}
