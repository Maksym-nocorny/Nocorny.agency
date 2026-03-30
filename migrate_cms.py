import csv
import os

# File paths
PORTFOLIO_CSV = 'NoCorny v2.1 Portfolios.csv'
FAQ_CSV = 'NoCorny v2.1 FAQs.csv'

INDEX_HTML = 'index.html'
PORTFOLIO_HTML = 'portfolio.html'
WEB_DESIGN_HTML = 'services/web-design.html'
WEBFLOW_DEV_HTML = 'services/webflow-development.html'

def load_csv(path):
    if not os.path.exists(path):
        print(f"CSV not found: {path}")
        return []
    with open(path, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_portfolio_html(item):
    name = item.get('Name', '')
    slug = item.get('Slug', '')
    thumbnail = item.get('Thumbnail Image', '')
    # Handle both full URLs and local paths
    img_url = thumbnail if thumbnail.startswith('http') else f"images/{thumbnail}"
    
    return f'''
    <div role="listitem" class="w-dyn-item">
      <div class="portf-card-wrapper">
        <a href="https://nocorny.agency/portfolio/{slug}" class="link-block-4 w-inline-block"></a>
        <div class="div-block-57">
          <img src="{img_url}" loading="lazy" style="opacity:1" alt="{name}" class="image-main">
          <img src="{img_url}" loading="lazy" alt="" class="image-bg">
        </div>
        <div class="div-block-58">
          <h3 class="landing-h4">{name}</h3>
          <div class="icon-embed-custom-28 w-embed">
            <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 40 40" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
              <path d="M26.674 15.69L12.329 30.035L9.97229 27.6783L24.3173 13.3333H11.6723V10H30.0056V28.3333H26.6723L26.674 15.69Z" fill="currentColor"></path>
            </svg>
          </div>
        </div>
      </div>
    </div>
    '''

def get_faq_html(item, index):
    question = item.get('Question', '')
    answer = item.get('Answer text', '')
    item_class = "faq-odd-item" if (index % 2 == 0) else "faq-even-item"
    
    return f'''
    <div role="listitem" class="{item_class} w-dyn-item">
      <div class="faq-wrapper">
        <div class="div-block-54">
          <div class="div-block-55">
            <div class="landing-h5 no-caps">{question}</div>
            <div class="faq-icon-wrap">
              <div class="icon-faq-arrow w-embed">
                <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
                  <path d="M4 16L12 8L20 16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
              </div>
            </div>
          </div>
          <p class="faq-answer">{answer}</p>
        </div>
        <div class="div-block-68"></div>
      </div>
    </div>
    '''

def replace_between(content, marker_start, marker_end, replacement):
    if marker_start not in content:
        return content
    
    parts = content.split(marker_start)
    new_parts = [parts[0] + marker_start + replacement]
    
    for part in parts[1:]:
        if marker_end in part:
            subparts = part.split(marker_end, 1)
            new_parts.append(marker_end + subparts[1])
        else:
            new_parts.append(part)
            
    return "".join(new_parts)

def process_file(html_path, portfolios=None, faqs=None):
    if not os.path.exists(html_path):
        return
        
    print(f"Processing {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Inject Portfolios
    if portfolios:
        html = replace_between(html, 
                               'class="collection-list-3 w-dyn-items">', 
                               '</div>\n                  <div class="w-dyn-empty">', 
                               portfolios)
        # Fallback if marker slightly different
        html = replace_between(html, 
                               'class="collection-list-3 w-dyn-items">', 
                               '</div>\n                <div class="w-dyn-empty">', 
                               portfolios)

    # 2. Inject FAQs
    if faqs:
        half = (len(faqs) + 1) // 2
        first_half = "".join(faqs[:half])
        second_half = "".join(faqs[half:])
        
        # In index.html, there are two separate lists
        if 'index.html' in html_path:
            # First FAQ block
            html = replace_between(html, 
                                   'class="collection-list-2 w-dyn-items">', 
                                   '</div>\n                  <div class="w-dyn-empty">', 
                                   first_half)
            # Second FAQ block (this is tricky because markers are identical)
            # We used replace_between that only works once if markers are unique, 
            # let's do a more careful split for index.html
            parts = html.split('class="collection-list-2 w-dyn-items">')
            if len(parts) >= 3:
                # Part 0: before first list
                # Part 1: between markers
                # Part 2: after second marker
                
                mid_parts = parts[1].split('</div>\n                  <div class="w-dyn-empty">', 1)
                end_parts = parts[2].split('</div>\n                  <div class="w-dyn-empty">', 1)
                
                html = (parts[0] + 'class="collection-list-2 w-dyn-items">' + first_half + 
                        '</div>\n                  <div class="w-dyn-empty">' + mid_parts[1] + 
                        'class="collection-list-2 w-dyn-items">' + second_half + 
                        '</div>\n                  <div class="w-dyn-empty">' + end_parts[1])
        else:
            # Service pages usually have one list
            html = replace_between(html, 
                                   'class="collection-list-2 w-dyn-items">', 
                                   '</div>\n                  <div class="w-dyn-empty">', 
                                   "".join(faqs))

    # 3. Fix 404 Image (Homepage only)
    if 'index.html' in html_path:
        html = html.replace('images/Frame-186-2.avif', 'images/Frame-1984078558.avif')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    portfolios_data = load_csv(PORTFOLIO_CSV)
    faqs_data = load_csv(FAQ_CSV)
    
    portfolio_html_all = "".join([get_portfolio_html(p) for p in portfolios_data])
    portfolio_html_featured = "".join([get_portfolio_html(p) for p in portfolios_data[:6]])
    
    faq_by_page = {}
    for f in faqs_data:
        page = f.get('Page', 'home')
        if page not in faq_by_page:
            faq_by_page[page] = []
        faq_by_page[page].append(f)
    
    # Run processing
    process_file(INDEX_HTML, 
                 portfolios=portfolio_html_featured, 
                 faqs=[get_faq_html(f, i) for i, f in enumerate(faq_by_page.get('home', []))])
                 
    process_file(PORTFOLIO_HTML, portfolios=portfolio_html_all)
    
    for page_key, path in [('web-design', WEB_DESIGN_HTML), ('webflow-development', WEBFLOW_DEV_HTML)]:
        process_file(path, faqs=[get_faq_html(f, i) for i, f in enumerate(faq_by_page.get(page_key, []))])

    print("Migration complete!")

if __name__ == '__main__':
    main()
