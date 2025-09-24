package modules.fooditem.dto;

import java.util.List;
import lombok.Data;
import org.springframework.data.domain.Page;

@Data
public class PagedResponse<T> {

  private List<T> content;

  private Integer page;

  private Integer pageSize;

  private Long totalElements;

  private Integer totalPages;

  private Boolean hasNext;

  private Boolean hasPrevious;

  public static <T> PagedResponse<T> fromPage(Page<T> page) {
    PagedResponse<T> response = new PagedResponse<>();
    response.setContent(page.getContent());
    response.setPage(page.getNumber() + 1); // Convert 0-based to 1-based
    response.setPageSize(page.getSize());
    response.setTotalElements(page.getTotalElements());
    response.setTotalPages(page.getTotalPages());
    response.setHasNext(page.hasNext());
    response.setHasPrevious(page.hasPrevious());
    return response;
  }
}