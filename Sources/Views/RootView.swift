import SwiftUI

enum Route: Hashable {
    case letter(String)
    case term(Term)
    case lens(LensConfig)
    case favorites
    case about
}

struct RootView: View {
    @EnvironmentObject var store: GlossaryStore
    @EnvironmentObject var purchases: PurchaseManager
    let onSwitchIndustry: () -> Void
    @State private var query: String = ""
    @State private var filter = FilterState()
    @State private var showingFilter = false
    @State private var showingPaywall = false
    @State private var path: [Route] = []

    private let columns = Array(repeating: GridItem(.flexible(minimum: 50), spacing: 6), count: 4)

    var body: some View {
        NavigationStack(path: $path) {
            ZStack {
                PGBackground()
                VStack(spacing: 0) {
                    if shouldShowEditorialHeader {
                        EditorialHeader(brand: .current, entryCount: store.allTerms.count)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal, 20)
                            .padding(.top, 8)
                            .padding(.bottom, 16)
                    }

                    PGSearchBar(text: $query)
                        .padding(.horizontal, 20)
                        .padding(.bottom, 12)

                    content
                }
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(PGColors.bg, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        onSwitchIndustry()
                    } label: {
                        Image(systemName: "square.grid.2x2")
                            .font(.system(size: 17, weight: .semibold))
                            .foregroundStyle(PGColors.accent)
                    }
                    .accessibilityLabel("Switch industry")
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingFilter = true
                    } label: {
                        Image(systemName: filter.isActive
                              ? "line.3.horizontal.decrease.circle.fill"
                              : "line.3.horizontal.decrease.circle")
                            .font(.system(size: 19, weight: .semibold))
                            .foregroundStyle(PGColors.accent)
                    }
                    .accessibilityLabel("Filter")
                }
            }
            .sheet(isPresented: $showingFilter) {
                FilterSheet(
                    filter: $filter,
                    onSelectLens: { lens in
                        showingFilter = false
                        path.append(.lens(lens))
                    },
                    onSelectAbout: {
                        showingFilter = false
                        path.append(.about)
                    }
                )
                .presentationDetents([.large])
            }
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .letter(let letter):
                    LetterView(letter: letter)
                case .term(let term):
                    TermDetailView(term: term)
                case .lens(let lens):
                    LensView(lens: lens)
                case .favorites:
                    FavoritesView()
                case .about:
                    AboutView()
                }
            }
            .sheet(isPresented: $showingPaywall) {
                PaywallSheet(targetIndustry: store.industryID)
                    .environmentObject(purchases)
                    .presentationDetents([.large])
            }
        }
        .tint(PGColors.accent)
        .environment(\.openURL, OpenURLAction { url in
            if let term = store.term(matchingURL: url) {
                if purchases.isLocked(term, in: store.industryID) {
                    showingPaywall = true
                } else {
                    path.append(.term(term))
                }
                return .handled
            }
            return .systemAction
        })
        .task {
            // Test hook: when JBG_TEST_NAVIGATE=<term name> env var is set at launch,
            // auto-push that term onto the nav stack so QA can land on it without
            // tapping through the UI. Safe to ship — env var is never set in prod.
            if let target = ProcessInfo.processInfo.environment["JBG_TEST_NAVIGATE"],
               !target.isEmpty,
               let term = store.allTerms.first(where: { $0.term.caseInsensitiveCompare(target) == .orderedSame }) {
                path = [.term(term)]
            }
            // Test hook: when JBG_TEST_PAYWALL is set, immediately present the
            // paywall sheet for the current industry. Used for App Store
            // screenshot capture. Safe to ship — env var is never set in prod.
            if ProcessInfo.processInfo.environment["JBG_TEST_PAYWALL"] != nil {
                showingPaywall = true
            }
        }
    }

    private var shouldShowEditorialHeader: Bool {
        query.trimmingCharacters(in: .whitespaces).isEmpty && !filter.isActive
    }

    @ViewBuilder
    private var content: some View {
        if !query.trimmingCharacters(in: .whitespaces).isEmpty {
            searchResults
        } else if filter.isActive {
            filteredResults
        } else {
            alphabetGrid
        }
    }

    private var alphabetGrid: some View {
        ScrollView {
            VStack(spacing: 12) {
                NavigationLink(value: Route.favorites) {
                    FavoritesHeroCard(count: store.favorites.count)
                }
                .buttonStyle(.plain)
                .padding(.horizontal, 20)
                .padding(.top, 4)

                LazyVGrid(columns: columns, spacing: 6) {
                    ForEach(store.alphabetLetters, id: \.self) { letter in
                        let count = store.byLetter[letter]?.count ?? 0
                        let isLocked = purchases.isLocked(letter: letter, in: store.industryID)
                        if isLocked {
                            Button {
                                showingPaywall = true
                            } label: {
                                LetterTile(letter: letter, count: count)
                                    .lockedAffordance(true, iconAlignment: .topTrailing)
                            }
                            .buttonStyle(.plain)
                        } else {
                            NavigationLink(value: Route.letter(letter)) {
                                LetterTile(letter: letter, count: count)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 24)
            }
        }
        .scrollDismissesKeyboard(.immediately)
    }

    private var searchResults: some View {
        let results = store.search(query)
        return Group {
            if results.isEmpty {
                ContentUnavailableView.search(text: query)
            } else {
                List(results) { term in
                    lockableTermRow(term: term)
                        .listRowBackground(PGColors.card)
                        .listRowSeparatorTint(PGColors.inkRule)
                }
                .listStyle(.plain)
                .scrollContentBackground(.hidden)
            }
        }
    }

    @ViewBuilder
    private func lockableTermRow(term: Term) -> some View {
        let isLocked = purchases.isLocked(term, in: store.industryID)
        if isLocked {
            Button {
                showingPaywall = true
            } label: {
                TermRow(term: term).lockedAffordance(true)
            }
            .buttonStyle(.plain)
        } else {
            NavigationLink(value: Route.term(term)) {
                TermRow(term: term)
            }
        }
    }

    private var filteredResults: some View {
        let results = store.filtered(by: filter)
        return VStack(spacing: 0) {
            FilterPill(filter: filter, count: results.count) {
                filter = FilterState()
            }
            .padding(.horizontal, 16)
            .padding(.top, 8)
            .padding(.bottom, 4)

            if results.isEmpty {
                Spacer()
                VStack(spacing: 10) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 32))
                        .foregroundStyle(PGColors.inkFaint)
                    Text("No terms match these filters")
                        .font(PGFont.termRowTitle)
                        .foregroundStyle(PGColors.ink)
                    Button("Clear filters") { filter = FilterState() }
                        .font(PGFont.buttonLabel)
                        .foregroundStyle(PGColors.accent)
                }
                Spacer()
                Spacer()
            } else {
                List(results) { term in
                    lockableTermRow(term: term)
                        .listRowBackground(PGColors.card)
                        .listRowSeparatorTint(PGColors.inkRule)
                }
                .listStyle(.plain)
                .scrollContentBackground(.hidden)
            }
        }
    }
}

private struct FilterPill: View {
    let filter: FilterState
    let count: Int
    let onClear: () -> Void

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "line.3.horizontal.decrease.circle.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(PGColors.bg)
            Text(filter.summary)
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(PGColors.bg)
                .lineLimit(1)
            Text("· \(count)")
                .font(PGFont.chipCountItalic)
                .foregroundStyle(PGColors.accentTint)
            Spacer()
            Button(action: onClear) {
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 16))
                    .foregroundStyle(PGColors.bg.opacity(0.85))
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Clear filters")
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(PGColors.ink, in: Capsule())
    }
}

private struct FavoritesHeroCard: View {
    let count: Int

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: count > 0 ? "star.fill" : "star")
                .font(.system(size: 22, weight: .semibold))
                .foregroundStyle(PGColors.accent)
                .frame(width: 44, height: 44)
                .background(
                    Circle().fill(PGColors.accent.opacity(0.10))
                )

            VStack(alignment: .leading, spacing: 2) {
                Text("Favorites")
                    .font(PGFont.termRowTitle)
                    .foregroundStyle(PGColors.ink)
                Text(count == 0 ? "Tap the star on any term to save" : "\(count) saved")
                    .font(PGFont.metaItalic)
                    .foregroundStyle(PGColors.inkLight)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(PGColors.inkFaint)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(PGColors.card)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(PGColors.cardBorder, lineWidth: 1)
        )
    }
}

private struct LetterTile: View {
    let letter: String
    let count: Int

    var body: some View {
        VStack(spacing: 2) {
            Text(letter)
                .font(PGFont.letterTileItalic)
                .foregroundStyle(PGColors.ink)
            Text("\(count)")
                .font(PGFont.tileCount)
                .foregroundStyle(PGColors.inkFaint)
        }
        .frame(maxWidth: .infinity, minHeight: 56)
        .padding(.vertical, 4)
        .background(
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .fill(PGColors.card)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .stroke(PGColors.cardBorder, lineWidth: 1)
        )
    }
}

struct TermRow: View {
    let term: Term

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(term.term)
                .font(PGFont.termRowTitle)
                .foregroundStyle(PGColors.ink)
            if term.hasFull {
                Text(term.full)
                    .font(PGFont.termRowFullItalic)
                    .foregroundStyle(PGColors.inkLight)
            }
        }
        .padding(.vertical, 4)
    }
}
