import SwiftUI

struct AboutView: View {
    var body: some View {
        ZStack {
            PGBackground()
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    disclaimer
                    sources
                    trademarks
                    Spacer(minLength: 24)
                }
                .padding(.horizontal, 20)
                .padding(.top, 12)
            }
        }
        .navigationTitle("About")
        .navigationBarTitleDisplayMode(.inline)
    }

    private var disclaimer: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("ABOUT")
                .font(PGFont.eyebrow)
                .tracking(1.8)
                .foregroundStyle(PGColors.accent)

            ForEach(Brand.current.aboutParagraphs, id: \.self) { paragraph in
                Text(paragraph)
                    .font(PGFont.body)
                    .foregroundStyle(PGColors.ink)
                    .lineSpacing(3)
            }

            if !Brand.current.aboutDisclaimer.isEmpty {
                Text(Brand.current.aboutDisclaimer)
                    .font(PGFont.snappyItalic)
                    .foregroundStyle(PGColors.accent)
                    .padding(.top, 4)
            }
        }
    }

    private var sources: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("SOURCES")
                .font(PGFont.eyebrow)
                .tracking(1.8)
                .foregroundStyle(PGColors.accent)
                .padding(.top, 8)

            ForEach(Brand.current.aboutSources, id: \.heading) { group in
                sourceGroup(heading: group.heading, items: group.items)
            }
        }
    }

    /// Universal trademark / non-affiliation notice. Applies across every industry,
    /// so it lives here in the shared About screen rather than per-brand. Brand,
    /// company, and product names are referenced for editorial/reference purposes only.
    private var trademarks: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("TRADEMARKS")
                .font(PGFont.eyebrow)
                .tracking(1.8)
                .foregroundStyle(PGColors.accent)
                .padding(.top, 8)

            Text("Trademarks, brand names, and product names are the property of their respective owners. This app is an independent educational reference and is not affiliated with, sponsored by, or endorsed by any company, product, or organization mentioned.")
                .font(PGFont.metaItalic)
                .foregroundStyle(PGColors.inkLight)
                .lineSpacing(2)
        }
    }

    private func sourceGroup(heading: String, items: [String]) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(heading)
                .font(PGFont.policyTitle)
                .foregroundStyle(PGColors.ink)
            ForEach(items, id: \.self) { item in
                Text(LocalizedStringKey(linkifiedSource(item)))
                    .font(PGFont.body)
                    .foregroundStyle(PGColors.inkLight)
                    .tint(PGColors.accent)
                    .lineSpacing(2)
                    .accessibilityHint("Opens \(item) website in browser.")
            }
        }
    }

    /// Linkify an About-screen source item. Two formats supported:
    ///   "FDA — Food and Drug Administration" → "[FDA](url) — Food and Drug Administration"
    ///   "OpenAI"                              → "[OpenAI](url)"
    /// If no key matches, returns the item unchanged.
    private func linkifiedSource(_ item: String) -> String {
        let urls = Brand.current.sourceURLs
        if let dashRange = item.range(of: " — ") {
            let abbrev = String(item[..<dashRange.lowerBound])
            let rest = String(item[dashRange.lowerBound...])
            if let url = urls[abbrev] {
                return "[\(abbrev)](\(url.absoluteString))\(rest)"
            }
            return item
        }
        if let url = urls[item] {
            return "[\(item)](\(url.absoluteString))"
        }
        return item
    }
}

#Preview {
    NavigationStack { AboutView() }
}
