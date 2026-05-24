import SwiftUI

struct EditorialHeader: View {
    let brand: Brand
    let entryCount: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text(brand.titlePrefix)
                    .font(PGFont.jbStamp)
                    .foregroundStyle(PGColors.ink)
                Text(brand.titleBody)
                    .font(PGFont.displayItalic)
                    .foregroundStyle(brand.primaryColor)
            }

            Text("\(entryCount) \(brand.entryNoun)")
                .font(PGFont.metaItalic)
                .foregroundStyle(PGColors.inkLight)

            if let tagline = brand.tagline {
                Text(tagline)
                    .font(PGFont.metaItalic)
                    .foregroundStyle(PGColors.inkLight)
                    .padding(.top, 2)
            }
        }
    }
}

#Preview("JB Pharma") {
    EditorialHeader(brand: .current, entryCount: 415)
        .padding()
        .background(PGColors.bg)
}

#Preview("JB Finance — templating proof") {
    EditorialHeader(
        brand: Brand(
            appStoreName: "JB Finance Glossary",
            displayName: "JB Finance",
            navigationTitle: "JB Finance",
            titlePrefix: "JB",
            titleBody: "Finance",
            subtitle: "decoding equities jargon",
            tagline: "An equities reference for generalists",
            entryNoun: "ratios",
            dataResource: "finance",
            primaryColor: Color(red: 0.13, green: 0.30, blue: 0.42),
            primaryDarkColor: Color(red: 0.10, green: 0.22, blue: 0.32),
            bgColor: PGColors.bg,
            urlScheme: "finance",
            aboutParagraphs: [],
            aboutDisclaimer: "",
            aboutSources: [],
            lenses: [],
            accentTint: nil,
            sourceURLs: [:]
        ),
        entryCount: 312
    )
    .padding()
    .background(PGColors.bg)
}
